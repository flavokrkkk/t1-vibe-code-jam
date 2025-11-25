from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any
from uuid import uuid4

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from langchain_integration import get_scibox_llm
from scibox_config import DEFAULT_CHAT_MODEL

logger = logging.getLogger(__name__)


def get_system_prompt(job_title: str, required_skills: list[str], amount_of_tasks: int) -> str:
    """Генерация системного промпта для интервью."""
    skills_text = ", ".join(required_skills) if required_skills else "не указаны"
    
    return f"""/no_think Ты профессиональный интервьюер, проводящий техническое интервью для вакансии "{job_title}".

Твоя задача:
1. Провести структурированное интервью, оценивая кандидата по следующим навыкам: {skills_text}
2. Задать примерно {amount_of_tasks} основных вопросов/задач, связанных с этими навыками
3. Анализировать ответы кандидата, задавая уточняющие вопросы при необходимости
4. Самостоятельно решить, когда интервью достаточно полное для оценки кандидата
5. В конце интервью предоставить развернутую обратную связь

Правила проведения интервью:
- Будь дружелюбным и профессиональным
- Задавай вопросы последовательно, не перескакивай с темы на тему
- ВСЕГДА помни контекст предыдущих вопросов и ответов - НЕ начинай интервью заново, НЕ задавай первый вопрос повторно
- Если кандидат ответил на твой вопрос - анализируй его ответ и либо задавай уточняющий вопрос, либо переходи к следующему вопросу
- Если ответ неполный или требует уточнения, задавай уточняющие вопросы для получения дополнительной информации
- Оценивай не только технические знания, но и способ мышления и подход к решению задач
- После каждого ответа кандидата давай краткую обратную связь (1-2 предложения) и СРАЗУ задавай следующий вопрос в ОДНОМ сообщении
- Формат: сначала краткая обратная связь по ответу, затем следующий вопрос
- НЕ разделяй обратную связь и следующий вопрос на отдельные сообщения - они должны быть вместе
- Когда задал примерно {amount_of_tasks} основных вопросов ИЛИ если кандидат не знает ответы на 3-4 вопроса подряд - ОБЯЗАТЕЛЬНО заверши интервью фразой: "[ЗАВЕРШЕНИЕ ИНТЕРВЬЮ]"
- НЕ задавай один и тот же вопрос повторно - если кандидат не знает ответ, переходи к следующей теме
- НЕ задавай вопросы по темам, которые уже были покрыты
- Если кандидат не знает ответы на несколько вопросов подряд (3-4), это сигнал к завершению интервью
- После завершения интервью предоставь итоговую обратную связь

ВАЖНО:
- Говори напрямую с кандидатом, как настоящий интервьюер
- НЕ показывай свои размышления, мета-комментарии или объяснения своих действий
- НЕ пиши фразы типа "Чтобы прояснить ситуацию", "Цель этих вопросов", "Я могу задать дополнительные вопросы"
- Просто задавай вопросы и давай комментарии естественным образом
- Не объясняй, зачем ты задаешь вопрос - просто задавай его
- КРИТИЧЕСКИ ВАЖНО: Анализируй ТОЛЬКО то, что кандидат реально сказал в своем ответе. НЕ придумывай, что кандидат мог сказать или имел в виду. Если кандидат ответил "не знаю" или "не помню" - признай это честно, не приписывай ему знания, которых он не показал
- Если кандидат не ответил на вопрос или ответил "не знаю" - либо задай более простой вопрос по той же теме, либо переходи к другой теме, но НЕ придумывай ответы за кандидата

Формат итоговой обратной связи должен включать:
- Общую оценку кандидата
- Оценку по каждому требуемому навыку
- Сильные стороны
- Области для улучшения
- Рекомендации

Начинай интервью с приветствия и первого вопроса."""


def run_code_tests(user_code: str, test_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Запуск тестов кода и возврат результатов."""
    results = []
    
    for test_case in test_cases:
        test_id = test_case.get("id", str(uuid4()))
        test_input = test_case.get("input", "")
        expected_output = test_case.get("expected_output", "")
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(user_code)
                temp_file = f.name
            
            try:
                process = subprocess.run(
                    ['python', temp_file],
                    input=test_input,
                    text=True,
                    capture_output=True,
                    timeout=5
                )
                
                actual_output = process.stdout.strip()
                details = None
                
                if process.stderr:
                    details = process.stderr.strip()
                    status = "ERROR"
                elif actual_output == expected_output:
                    status = "PASSED"
                else:
                    status = "FAILED"
                    details = f"Ожидалось: {expected_output}, получено: {actual_output}"
                    
            except subprocess.TimeoutExpired:
                status = "ERROR"
                details = "Превышено время выполнения (5 секунд)"
            except Exception as e:
                status = "ERROR"
                details = str(e)
            finally:
                Path(temp_file).unlink(missing_ok=True)
                
        except Exception as e:
            status = "ERROR"
            details = f"Ошибка при запуске теста: {str(e)}"
        
        results.append({
            "test_id": test_id,
            "status": status,
            "details": details
        })
    
    return results


class InterviewAgent:
    """ИИ-агент для проведения интервью с использованием LangChain."""

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_CHAT_MODEL):
        """Инициализация агента."""
        if api_key is None:
            api_key = os.getenv("SCIBOX_API_KEY")
        if not api_key:
            raise ValueError("SciBox API key обязателен. Установите SCIBOX_API_KEY или передайте api_key.")
        
        self.llm = get_scibox_llm(model=model)
        self.model_name = model
        self.conversation_history: list[Any] = []
        self.interview_ended = False
        self.amount_of_tasks = 0
        self.job_title = ""
        self.required_skills: list[str] = []
        self.code_submit_count: dict[str, int] = {}
        self.questions_asked = 0
        self.negative_answers_count = 0

    def _get_messages_with_history(self, user_input: str) -> list:
        """Создание списка сообщений с полной историей для диалогового режима."""
        system_prompt = get_system_prompt(
            self.job_title,
            self.required_skills,
            self.amount_of_tasks
        )
        
        messages = [SystemMessage(content=system_prompt)]
        
        for msg in self.conversation_history:
            if isinstance(msg, (HumanMessage, AIMessage)):
                cleaned_msg = msg
                if isinstance(msg, AIMessage):
                    content_cleaned = re.sub(r'<think>.*?</think>', '', msg.content, flags=re.DOTALL | re.IGNORECASE)
                    content_cleaned = re.sub(r'<reasoning>.*?</reasoning>', '', content_cleaned, flags=re.DOTALL | re.IGNORECASE)
                    if content_cleaned != msg.content:
                        cleaned_msg = AIMessage(content=content_cleaned.strip())
                messages.append(cleaned_msg)
        
        messages.append(HumanMessage(content=user_input))
        return messages

    def _check_interview_end(self, response: str) -> bool:
        """Проверка, завершил ли агент интервью."""
        end_markers = [
            "[ЗАВЕРШЕНИЕ ИНТЕРВЬЮ]",
            "[END_INTERVIEW]",
            "завершим интервью",
            "завершаем интервью",
            "завершить интервью",
            "закончим интервью",
            "заканчиваем интервью",
        ]
        response_upper = response.upper()
        return any(marker.upper() in response_upper for marker in end_markers)

    def _parse_ai_response(self, response_text: str) -> dict[str, Any]:
        """Парсинг ответа ИИ для извлечения структурированных данных."""
        feedback_match = re.search(r'ФИДБЭК:\s*(.+?)(?=\n|$)', response_text, re.IGNORECASE | re.DOTALL)
        score_match = re.search(r'ОЦЕНКА:\s*(\d+)', response_text, re.IGNORECASE)
        
        feedback = feedback_match.group(1).strip() if feedback_match else None
        score = int(score_match.group(1)) if score_match else None
        
        if score is not None:
            score = max(0, min(100, score))
        
        return {
            "feedback": feedback,
            "score": score,
            "text": response_text
        }

    def start_interview(
        self,
        job_title: str,
        required_skills: list[str],
        amount_of_tasks: int,
    ) -> dict[str, Any]:
        """Начало интервью - получение первого вопроса в формате STEP."""
        self.job_title = job_title
        self.required_skills = required_skills
        self.amount_of_tasks = amount_of_tasks
        self.interview_ended = False
        self.conversation_history = []
        self.code_submit_count = {}
        self.questions_asked = 0
        self.negative_answers_count = 0
        
        messages = [
            SystemMessage(content=get_system_prompt(
                self.job_title,
                self.required_skills,
                self.amount_of_tasks
            )),
            HumanMessage(content="Начни интервью. Представься и задай первый вопрос кандидату.")
        ]
        
        response = self.llm.invoke(messages)
        first_question = response.content if hasattr(response, 'content') else str(response)
        if not first_question:
            raise RuntimeError("Пустой ответ от модели")
        
        first_question_cleaned = re.sub(r'<think>.*?</think>', '', first_question, flags=re.DOTALL | re.IGNORECASE)
        first_question_cleaned = re.sub(r'<reasoning>.*?</reasoning>', '', first_question_cleaned, flags=re.DOTALL | re.IGNORECASE)
        first_question_cleaned = first_question_cleaned.strip()
        
        if not first_question_cleaned:
            first_question_cleaned = first_question
        
        self.conversation_history.append(HumanMessage(content="Начни интервью"))
        self.conversation_history.append(AIMessage(content=first_question_cleaned))
        self.questions_asked = 1
        
        return {
            "type": "DIALOG",
            "question_text": first_question_cleaned,
            "status": "IN_PROGRESS",
            "score": None,
            "ai_feedback": None,
            "user_answer": None,
            "feedback": None
        }

    def process_answer(self, user_answer: str) -> dict[str, Any]:
        """Обработка ответа кандидата и получение следующего вопроса в формате STEP."""
        if self.interview_ended:
            return {
                "type": "DIALOG",
                "question_text": "Интервью уже завершено.",
                "status": "COMPLETED",
                "score": None,
                "ai_feedback": None,
                "user_answer": user_answer,
                "feedback": None
            }
        
        last_question = ""
        if len(self.conversation_history) >= 2:
            last_ai_msg = self.conversation_history[-1]
            if isinstance(last_ai_msg, AIMessage):
                last_question = last_ai_msg.content[:200]
        
        user_answer_lower = user_answer.lower().strip()
        is_negative_answer = any(phrase in user_answer_lower for phrase in [
            "не знаю", "не помню", "не знаю разницы", "не понимаю", 
            "не могу", "не умею", "не знаю как", "не помню как",
            "не использовал", "не использовал типы", "не работал",
            "не знаю что", "не помню что", "не знаю как это",
            "не знаю об этом", "не знаком", "не знаком с"
        ])
        
        if is_negative_answer:
            self.negative_answers_count += 1
        else:
            self.negative_answers_count = 0
        
        should_end = (
            self.questions_asked >= self.amount_of_tasks or
            self.negative_answers_count >= 3
        )
        
        next_question_num = self.questions_asked + 1
        context_info = f"Уже задано вопросов: {self.questions_asked}/{self.amount_of_tasks}. Следующий вопрос будет номер {next_question_num}. Отрицательных ответов подряд: {self.negative_answers_count}."
        
        if is_negative_answer:
            input_prompt = f"""{context_info}

Кандидат ответил на твой вопрос '{last_question}' следующим образом: '{user_answer}'.

КРИТИЧЕСКИ ВАЖНО: Кандидат сказал, что НЕ ЗНАЕТ/НЕ ИСПОЛЬЗОВАЛ/НЕ РАБОТАЛ. Это означает:
- Кандидат НЕ упомянул никаких технических деталей
- Кандидат НЕ дал правильного ответа
- Кандидат НЕ показал знаний по этой теме
- Кандидат НЕ говорил про NumPy, массивы, типы данных, производительность и т.д. - если он этого не упомянул

ТВОЯ ЗАДАЧА:
1. Признай честно, что кандидат не знает ответа (1 предложение)
2. СРАЗУ задай следующий вопрос в том же сообщении
3. НЕ придумывай, что кандидат мог сказать
4. НЕ хвали кандидата за ответ, которого он не дал
5. НЕ упоминай технические термины, которые кандидат НЕ использовал в своем ответе
6. Либо задай более простой вопрос по этой теме, либо переходи к другой теме
7. Будь тактичным, но честным

Пример правильного формата:
"Понятно, что вы не знаете ответа на этот вопрос. Давайте попробуем другой вопрос: [вопрос]"

ВАЖНО:
- НЕ пиши "Первый вопрос" или "Вопрос 1" - это уже {next_question_num}-й вопрос
- НЕ нумеруй вопросы явно, просто задавай их естественно
- НЕ повторяй вопросы, которые уже задавал

ЗАПРЕЩЕНО писать:
- "Хорошо, вы правильно отметили..." если кандидат ничего не отметил
- "Вы упомянули NumPy..." если кандидат не упоминал NumPy
- "Это демонстрирует понимание..." если кандидат не показал понимания
- Любые положительные оценки, если кандидат сказал "не знаю" или "не использовал"

НЕ разделяй обратную связь и вопрос на отдельные сообщения.

{'ВНИМАНИЕ: Уже задано достаточно вопросов или кандидат не знает ответы на несколько вопросов подряд. СЛЕДУЮЩИЙ ШАГ - заверши интервью фразой "[ЗАВЕРШЕНИЕ ИНТЕРВЬЮ]" и предоставь итоговую обратную связь.' if should_end else ''}"""
        else:
            input_prompt = f"""{context_info}

Кандидат ответил на твой предыдущий вопрос '{last_question}' следующим образом: '{user_answer}'.

ТВОЯ ЗАДАЧА:
1. Дай краткую обратную связь по ответу кандидата (1-2 предложения) - что хорошо, что можно улучшить
2. СРАЗУ задай следующий вопрос в том же сообщении
3. НЕ разделяй обратную связь и вопрос на отдельные сообщения - они должны быть вместе
4. Если ответ требует уточнения - дай обратную связь и задай уточняющий вопрос
5. Если ответ хороший и полный - дай положительную обратную связь и переходи к следующему вопросу по навыкам

Пример правильного формата:
"Хороший ответ, вы правильно упомянули основные особенности. Теперь следующий вопрос: [вопрос]"

ВАЖНО:
- НЕ пиши "Первый вопрос" или "Вопрос 1" - это уже {next_question_num}-й вопрос
- НЕ нумеруй вопросы явно, просто задавай их естественно
- НЕ повторяй вопросы, которые уже задавал

НЕ делай так:
"Отлично! Вы дали хороший ответ. Теперь давайте перейдем к SQL.
Вопрос 2: [вопрос]"

НЕ начинай интервью заново.

{'ВНИМАНИЕ: Уже задано достаточно вопросов. СЛЕДУЮЩИЙ ШАГ - заверши интервью фразой "[ЗАВЕРШЕНИЕ ИНТЕРВЬЮ]" и предоставь итоговую обратную связь.' if should_end else ''}"""
        
        messages = self._get_messages_with_history(input_prompt)
        response = self.llm.invoke(messages)
        ai_response = response.content if hasattr(response, 'content') else str(response)
        if not ai_response:
            raise RuntimeError("Пустой ответ от модели")
        
        if self._check_interview_end(ai_response):
            self.interview_ended = True
            ai_response = re.sub(r'\[ЗАВЕРШЕНИЕ ИНТЕРВЬЮ\]|\[END_INTERVIEW\]', '', ai_response, flags=re.IGNORECASE).strip()
        
        ai_response_cleaned = re.sub(r'<think>.*?</think>', '', ai_response, flags=re.DOTALL | re.IGNORECASE)
        ai_response_cleaned = re.sub(r'<think>.*?</think>', '', ai_response_cleaned, flags=re.DOTALL | re.IGNORECASE)
        ai_response_cleaned = re.sub(r'<reasoning>.*?</reasoning>', '', ai_response_cleaned, flags=re.DOTALL | re.IGNORECASE)
        ai_response_cleaned = ai_response_cleaned.strip()
        
        if not ai_response_cleaned:
            ai_response_cleaned = ai_response
        
        if is_negative_answer:
            negative_phrases = [
                "правильно отметил", "правильно упомянул", "правильно сказал",
                "отличный ответ", "хороший ответ", "ты правильно",
                "ты упомянул", "ты отметил", "ты сказал", "вы правильно",
                "вы упомянули", "вы отметили", "вы сказали", "хорошо, вы правильно",
                "вы дали хороший ответ", "вы правильно отметили", "демонстрирует понимание",
                "это демонстрирует", "преимущества", "по сравнению", "numpy", "массивы"
            ]
            response_lower = ai_response_cleaned.lower()
            
            user_words = set(re.findall(r'\b\w+\b', user_answer_lower))
            response_words = set(re.findall(r'\b\w+\b', response_lower))
            
            has_positive_feedback = any(phrase in response_lower for phrase in negative_phrases)
            mentions_user_content = len(user_words & response_words) > 2
            
            if has_positive_feedback and not mentions_user_content:
                logger.warning(f"Модель приписала ответ кандидату. Ответ кандидата: '{user_answer}', ответ модели: '{ai_response_cleaned[:200]}'")
                ai_response_cleaned = f"Понятно, что вы не знаете ответа на этот вопрос. Давайте попробуем другой вопрос или перейдем к другой теме."
        
        self.conversation_history.append(HumanMessage(content=user_answer))
        self.conversation_history.append(AIMessage(content=ai_response_cleaned))
        
        if not self._check_interview_end(ai_response_cleaned):
            self.questions_asked += 1
        
        if should_end and not self.interview_ended:
            self.interview_ended = True
            logger.info(f"Интервью завершено автоматически: вопросов {self.questions_asked}, отрицательных ответов подряд {self.negative_answers_count}")
        
        parsed = self._parse_ai_response(ai_response_cleaned)
        
        if self.interview_ended and "[ЗАВЕРШЕНИЕ ИНТЕРВЬЮ]" in ai_response_cleaned:
            ai_response_cleaned = re.sub(r'\[ЗАВЕРШЕНИЕ ИНТЕРВЬЮ\]|\[END_INTERVIEW\]', '', ai_response_cleaned, flags=re.IGNORECASE).strip()
            final_feedback = self.generate_feedback()
            ai_response_cleaned = f"{ai_response_cleaned}\n\n{final_feedback}"
        
        return {
            "type": "DIALOG",
            "question_text": ai_response_cleaned,
            "status": "COMPLETED" if self.interview_ended else "IN_PROGRESS",
            "score": parsed.get("score"),
            "ai_feedback": parsed.get("feedback") or ai_response_cleaned,
            "user_answer": user_answer,
            "feedback": parsed.get("feedback")
        }

    def process_code_submission(
        self,
        user_code: str,
        test_cases: list[dict[str, Any]],
        step_id: str,
        task_description: str = ""
    ) -> dict[str, Any]:
        """Обработка отправки кода: запуск тестов, фидбэк модели, формирование STEP."""
        if step_id not in self.code_submit_count:
            self.code_submit_count[step_id] = 0
        
        self.code_submit_count[step_id] += 1
        
        if self.code_submit_count[step_id] > 3:
            return {
                "type": "CODE_TASK",
                "status": "COMPLETED",
                "user_code": user_code,
                "code_test_results": [],
                "code_feedback": "Превышено максимальное количество попыток (3).",
                "code_score": 0,
                "score": 0,
                "ai_feedback": "Превышено максимальное количество попыток."
            }
        
        test_results = run_code_tests(user_code, test_cases)
        
        passed_count = sum(1 for r in test_results if r["status"] == "PASSED")
        total_count = len(test_results)
        test_summary = f"Пройдено тестов: {passed_count}/{total_count}"
        
        test_results_text = "\n".join([
            f"Тест {r['test_id']}: {r['status']}" + (f" - {r['details']}" if r.get('details') else "")
            for r in test_results
        ])
        
        prompt = f"""Кандидат отправил код для задачи: {task_description}

Код кандидата:
```python
{user_code}
```

Результаты тестов:
{test_summary}
{test_results_text}

Проанализируй код и результаты тестов. Дай фидбэк по коду, укажи что хорошо, что можно улучшить. Если тесты не прошли, объясни почему. Оцени код от 0 до 100.

Формат ответа:
ФИДБЭК: [твой фидбэк по коду]
ОЦЕНКА: [число от 0 до 100]"""
        
        messages = self._get_messages_with_history(prompt)
        response = self.llm.invoke(messages)
        ai_response = response.content if hasattr(response, 'content') else str(response)
        parsed = self._parse_ai_response(ai_response)
        
        code_score = parsed.get("score", 0)
        if code_score is None:
            code_score = int((passed_count / total_count) * 100) if total_count > 0 else 0
        
        status = "COMPLETED" if passed_count == total_count and total_count > 0 else "IN_PROGRESS"
        
        return {
            "type": "CODE_TASK",
            "status": status,
            "user_code": user_code,
            "code_test_results": test_results,
            "code_feedback": parsed.get("feedback") or ai_response,
            "code_score": code_score,
            "score": code_score,
            "ai_feedback": parsed.get("feedback") or ai_response
        }

    def is_interview_complete(self) -> bool:
        """Проверка, завершено ли интервью."""
        return self.interview_ended

    def generate_feedback(self) -> str:
        """Генерация итоговой обратной связи на основе всего интервью."""
        prompt = "Интервью завершено. Предоставь итоговую обратную связь по кандидату, включая оценку по каждому навыку, сильные стороны, области для улучшения и рекомендации."
        
        messages = self._get_messages_with_history(prompt)
        response = self.llm.invoke(messages)
        return response.content if hasattr(response, 'content') else str(response)

    def reset(self):
        """Сброс истории разговора."""
        self.conversation_history = []
        self.interview_ended = False
        self.code_submit_count = {}
        self.questions_asked = 0
        self.negative_answers_count = 0
