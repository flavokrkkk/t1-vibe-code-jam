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
- Если ответ неполный или требует уточнения, задавай уточняющие вопросы для получения дополнительной информации
- Оценивай не только технические знания, но и способ мышления и подход к решению задач
- После каждого ответа давай краткую обратную связь или переходи к следующему вопросу
- Когда считаешь, что собрал достаточно информации для оценки (обычно после {amount_of_tasks} основных вопросов), заверши интервью фразой: "[ЗАВЕРШЕНИЕ ИНТЕРВЬЮ]"
- Не завершай интервью слишком рано - убедись, что получил достаточно информации по всем требуемым навыкам
- Можешь задавать несколько уточняющих вопросов подряд, если это необходимо для полной оценки

ВАЖНО:
- Говори напрямую с кандидатом, как настоящий интервьюер
- НЕ показывай свои размышления, мета-комментарии или объяснения своих действий
- НЕ пиши фразы типа "Чтобы прояснить ситуацию", "Цель этих вопросов", "Я могу задать дополнительные вопросы"
- Просто задавай вопросы и давай комментарии естественным образом
- Не объясняй, зачем ты задаешь вопрос - просто задавай его

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

    def _create_agent(self) -> AgentExecutor:
        """Создание LangChain агента с инструментами."""
        def analyze_answer(answer: str) -> str:
            """Анализирует ответ кандидата и возвращает краткую оценку."""
            return f"Ответ проанализирован: {answer[:100]}..."
        
        tools = [
            Tool(
                name="analyze_answer",
                func=analyze_answer,
                description="Анализирует ответ кандидата на вопрос интервью"
            ),
        ]
        
        system_prompt = get_system_prompt(
            self.job_title,
            self.required_skills,
            self.amount_of_tasks
        )
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessage(content="{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(self.llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=False)

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
        
        agent = self._create_agent()
        
        result = agent.invoke({
            "input": "Начни интервью. Представься и задай первый вопрос кандидату.",
            "chat_history": [] 
        })
        
        first_question = result.get("output", "")
        if not first_question:
            raise RuntimeError("Пустой ответ от модели")
        
        self.conversation_history.append(HumanMessage(content="Начни интервью"))
        self.conversation_history.append(AIMessage(content=first_question))
        
        return {
            "type": "DIALOG",
            "question_text": first_question,
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
        
        agent = self._create_agent()
        
        chat_history_messages = []
        for msg in self.conversation_history:
            if isinstance(msg, (HumanMessage, SystemMessage)):
                chat_history_messages.append(msg)
        
        result = agent.invoke({
            "input": f"Кандидат ответил: {user_answer}. Проанализируй ответ и продолжай интервью. Можешь задать уточняющие вопросы, если нужно. Если ответ хороший, можешь перейти к следующему вопросу.",
            "chat_history": chat_history_messages
        })
        
        ai_response = result.get("output", "")
        if not ai_response:
            raise RuntimeError("Пустой ответ от модели")
        
        if self._check_interview_end(ai_response):
            self.interview_ended = True
            ai_response = re.sub(r'\[ЗАВЕРШЕНИЕ ИНТЕРВЬЮ\]|\[END_INTERVIEW\]', '', ai_response, flags=re.IGNORECASE).strip()
        
        self.conversation_history.append(HumanMessage(content=user_answer))
        self.conversation_history.append(AIMessage(content=ai_response))
        
        parsed = self._parse_ai_response(ai_response)
        
        return {
            "type": "DIALOG",
            "question_text": ai_response,
            "status": "COMPLETED" if self.interview_ended else "IN_PROGRESS",
            "score": parsed.get("score"),
            "ai_feedback": parsed.get("feedback") or ai_response,
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
        
        agent = self._create_agent()
        
        chat_history_messages = []
        for msg in self.conversation_history:
            if isinstance(msg, (HumanMessage, AIMessage)):
                chat_history_messages.append(msg)
        
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
        
        result = agent.invoke({
            "input": prompt,
            "chat_history": chat_history_messages
        })
        
        ai_response = result.get("output", "")
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
        agent = self._create_agent()
        
        chat_history_messages = []
        for msg in self.conversation_history:
            if isinstance(msg, (HumanMessage, AIMessage)):
                chat_history_messages.append(msg)
        
        result = agent.invoke({
            "input": "Интервью завершено. Предоставь итоговую обратную связь по кандидату, включая оценку по каждому навыку, сильные стороны, области для улучшения и рекомендации.",
            "chat_history": chat_history_messages
        })
        
        return result.get("output", "")

    def reset(self):
        """Сброс истории разговора."""
        self.conversation_history = []
        self.interview_ended = False
        self.code_submit_count = {}
