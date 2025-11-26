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

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from langchain_integration import get_scibox_llm
from scibox_config import DEFAULT_CHAT_MODEL

logger = logging.getLogger(__name__)

InterviewStepType = {
    "DIALOG": "DIALOG",
    "CODE_TASK": "CODE_TASK",
}

ResponseType = {
    "DIALOG_RESPONSE": "dialog_response",
    "NEW_STEP": "new_step",
    "FINAL_FEEDBACK": "final_feedback",
}


def get_system_prompt(job_title: str, required_skills: list[str], amount_of_tasks: int) -> str:
    """Генерация системного промпта для интервью."""
    skills_text = ", ".join(required_skills) if required_skills else "не указаны"
    
    return f"""Ты — строгий ассистент интервью. Твоя задача — **всегда возвращать валидный JSON** в **обёртке ```json ... ```**.

### КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА:

1. **ОТВЕТ ДОЛЖЕН БЫТЬ ТОЛЬКО ОДНИМ JSON-ОБЪЕКТОМ** внутри ```json```.

2. **НИКАКОГО текста до, после или между** — только ```json {{ ... }} ```.

3. **ВСЕ строки должны быть закрыты** — если не успеваешь, **сократи текст**, но не обрывай кавычки.

4. **Максимальная длина answerText — 2 предложения (до 300 символов)**. Если длиннее — обрежь.

5. **testCases — не более 3 штук**. Если больше — выбери самые важные.

6. **Все обязательные поля должны быть** — не пропускай `score`, `feedback`, `nextStep`.

---

### ОСОБЫЕ ПРАВИЛА ПЕРЕХОДА К ЗАВЕРШЕНИЮ:

- **НИКОГДА не переходи в `final_feedback`, пока не пройдёт фаза "уточнения вопросов"**.

- После **последнего запланированного шага** (когда `currentStepIndex + 1 === {amount_of_tasks}`) **обязательно**:

  1. Заверши текущий шаг (`new_step` или `dialog_response`).

  2. **Затем** — **всегда** задай вопрос:  

     "У вас остались вопросы? Если нет — можем завершить интервью."  

     (используй `dialog_response`).

  3. Жди ответа пользователя.

  4. Если пользователь:

     - Говорит **"да"**, **"нет вопросов"**, **"можно завершать"** → переходи в `final_feedback`.

     - Задаёт **вопрос** → ответь на него, затем **снова** спроси:  

       "Ещё вопросы? Если нет — можем завершить." (через `dialog_response`).

- **Только после явного подтверждения завершения** — выдавай `final_feedback`.

---

### ТИПЫ ОТВЕТОВ (выбери один):

#### 1. dialog_response — продолжить диалог

- Используй для:

  - Ответов на вопросы пользователя.

  - Уточнения: "У вас остались вопросы? Если нет — можем завершить интервью."

- answerText: **1–2 предложения**, вежливо, профессионально.

```json
{{
  "type": "dialog_response",
  "answerText": "Да, в нашей команде используют TypeScript. У вас остались вопросы? Если нет — можем завершить интервью."
}}
```

#### 2. new_step — завершить шаг и дать новый

- Обязательно: `answerText`, `feedback`, `score`, `nextStep`

- **feedback**: **2 предложения** — что хорошо, что можно улучшить, конкретные примеры (до 400 символов). Если длиннее — обрежь.

- **answerText**: 1–2 предложения.

- **score**: 0–100.

- **nextStep.type**: `{InterviewStepType["DIALOG"]}` или `{InterviewStepType["CODE_TASK"]}`

**Пример (диалог):**

```json
{{
  "type": "new_step",
  "answerText": "Отличное объяснение хуков.",
  "feedback": "Кандидат уверенно объяснил useState, useEffect и useCallback. Пример с оптимизацией был точным. Можно было упомянуть useMemo для тяжёлых вычислений.",
  "score": 88,
  "nextStep": {{
    "type": "{InterviewStepType["DIALOG"]}",
    "questionText": "Как вы работаете с Context API?"
  }}
}}
```

**Пример (код):**

```json
{{
  "type": "new_step",
  "answerText": "Код прошёл тесты.",
  "feedback": "Решение использует useCallback и React.memo корректно. Компонент не перерендеривается при смене other. Можно было вынести handleIncrement в родитель для большей гибкости.",
  "score": 82,
  "nextStep": {{
    "type": "{InterviewStepType["CODE_TASK"]}",
    "codeTask": {{
      "topic": "React Hooks",
      "difficulty": "medium",
      "language": "javascript"
    }}
  }}
}}
```

**ВАЖНО для CODE_TASK:**
- НЕ пиши `description`, `initialCode`, `testCases` в `nextStep.codeTask`
- Только: `topic` (тема задачи), `difficulty` ("easy", "medium", "hard"), `language` ("python", "javascript", и т.д.)
- Полная задача будет сгенерирована отдельно через `/generate_task`

#### 3. final_feedback — **ТОЛЬКО ПОСЛЕ ПОДТВЕРЖДЕНИЯ ЗАВЕРШЕНИЯ**

- Обязательно: `answerText`, `feedback`, `score`, `overallFeedback`, `totalScore`

- **feedback** и **score** — за **последний шаг** (2–3 предложения).

- **overallFeedback**: **4–6 предложений** — сильные стороны, зоны роста, общие впечатления, рекомендации.

- **totalScore**: средневзвешенная оценка.

```json
{{
  "type": "final_feedback",
  "answerText": "Спасибо за интервью! Отличная работа.",
  "feedback": "Кодовая задача решена оптимально с использованием memo и callback. Логика ясна, тесты пройдены.",
  "score": 85,
  "overallFeedback": "Кандидат демонстрирует уверенное владение React и оптимизацией рендера. Понимание Zustand и Context API на высоком уровне. В алгоритмах есть пробелы, но это компенсируется сильной фронтенд-логикой. Рекомендуется к найму на позицию Middle Frontend. Удачи в дальнейших собеседованиях!",
  "totalScore": 86
}}
```

---

### ОСНОВЫВАЙСЯ НА:

- История чата

- Текущий шаг: отслеживается автоматически, индекс будет указан в каждом запросе

- План интервью: **{amount_of_tasks} шагов**

- Позиция: "{job_title}"

- Требуемые навыки: {skills_text}

- Статус: **не завершай, пока не будет подтверждения**

### ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА ДЛЯ ВАКАНСИЙ DEVELOPER:

- **Если в названии позиции указано "developer"** (в любом регистре), то **ОБЯЗАТЕЛЬНО** должен быть **минимум один шаг с типом `{InterviewStepType["CODE_TASK"]}`** в ходе интервью.

- Это правило имеет **высший приоритет** — даже если все остальные шаги диалоговые, **минимум один** должен быть кодовая задача.

---

**НАЧИНАЙ ОТВЕТ СРАЗУ С ```json** и **ЗАКАНЧИВАЙ ```** — без пояснений.

Начинай интервью с приветствия и первого вопроса (используй `new_step` с `nextStep.type = "{InterviewStepType["DIALOG"]}"`)."""


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
        self.waiting_for_completion_confirmation = False

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

    def _extract_json(self, text: str) -> dict[str, Any] | None:
        """Извлечение JSON из ответа модели."""
        patterns = [
            r'```json\s*(\{.*?\})\s*```',
            r'```json\s*(\{.*\})\s*```',
            r'```\s*(\{.*?\})\s*```',
            r'```\s*(\{.*\})\s*```',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    json_str = match.group(1)
                    parsed = json.loads(json_str)
                    return parsed
                except json.JSONDecodeError:
                    continue
        
        json_start = text.find('{')
        if json_start != -1:
            bracket_count = 0
            json_end = -1
            for i in range(json_start, len(text)):
                if text[i] == '{':
                    bracket_count += 1
                elif text[i] == '}':
                    bracket_count -= 1
                    if bracket_count == 0:
                        json_end = i + 1
                        break
            
            if json_end != -1:
                try:
                    json_str = text[json_start:json_end]
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
        
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            return None
    
    def _parse_ai_response(self, response_text: str) -> dict[str, Any]:
        """Парсинг JSON ответа модели."""
        parsed = self._extract_json(response_text)
        if not parsed:
            logger.warning(f"Не удалось извлечь JSON из ответа: {response_text[:200]}")
            return {
                "type": "dialog_response",
                "answerText": response_text[:300] if response_text else "Ошибка обработки ответа",
            }
        return parsed

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
        response_text = response.content if hasattr(response, 'content') else str(response)
        if not response_text:
            raise RuntimeError("Пустой ответ от модели")
        
        parsed = self._parse_ai_response(response_text)
        
        if parsed.get("type") == "new_step":
            next_step = parsed.get("nextStep", {})
            next_step_type = next_step.get("type", InterviewStepType["DIALOG"])
            question_text = next_step.get("questionText", parsed.get("answerText", ""))
            
            next_step_data = None
            if next_step_type == InterviewStepType["CODE_TASK"]:
                code_task = next_step.get("codeTask", {})
                next_step_data = {
                    "type": "CODE_TASK",
                    "code_task": {
                        "topic": code_task.get("topic", "Python"),
                        "difficulty": code_task.get("difficulty", "medium"),
                        "language": code_task.get("language", "python")
                    }
                }
            else:
                next_step_data = {
                    "type": "DIALOG",
                    "question_text": question_text
                }
            
            self.conversation_history.append(HumanMessage(content="Начни интервью"))
            self.conversation_history.append(AIMessage(content=response_text))
            self.questions_asked = 1
            
            return {
                "type": "DIALOG",
                "question_text": question_text,
                "status": "IN_PROGRESS",
                "score": parsed.get("score"),
                "ai_feedback": parsed.get("answerText"),
                "user_answer": None,
                "feedback": parsed.get("feedback"),
                "next_step": next_step_data
            }
        else:
            answer_text = parsed.get("answerText", response_text[:300])
            self.conversation_history.append(HumanMessage(content="Начни интервью"))
            self.conversation_history.append(AIMessage(content=response_text))
            
            return {
                "type": "DIALOG",
                "question_text": answer_text,
                "status": "IN_PROGRESS",
                "score": None,
                "ai_feedback": answer_text,
                "user_answer": None,
                "feedback": None,
                "next_step": {
                    "type": "DIALOG",
                    "question_text": answer_text
                }
            }

    def _parse_code_submission(self, user_answer: str) -> dict[str, Any] | None:
        """Парсинг структурированного ответа с кодом."""
        if "User Code:" not in user_answer or "System Execution Result:" not in user_answer:
            return None
        
        parsed = {}
        
        desc_match = re.search(r'Task Description:\s*(.+?)(?=\nTopic:|$)', user_answer, re.DOTALL | re.IGNORECASE)
        if desc_match:
            parsed["description"] = desc_match.group(1).strip()
        
        topic_match = re.search(r'Topic:\s*(.+?)(?=\n|User Code:)', user_answer, re.IGNORECASE)
        if topic_match:
            parsed["topic"] = topic_match.group(1).strip()
        
        code_match = re.search(r'User Code:\s*(.+?)(?=\nSystem Execution Result:|$)', user_answer, re.DOTALL | re.IGNORECASE)
        if code_match:
            parsed["user_code"] = code_match.group(1).strip()
        
        result_match = re.search(r'System Execution Result:\s*(.+?)(?=\n|$)', user_answer, re.DOTALL | re.IGNORECASE)
        if result_match:
            parsed["test_results"] = result_match.group(1).strip()
        
        return parsed if parsed else None

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
                "feedback": None,
                "next_step": None
            }
        
        code_submission = self._parse_code_submission(user_answer)
        if code_submission:
            input_prompt = f"""Кандидат отправил код для задачи.

Описание задачи: {code_submission.get('description', 'Не указано')}
Тема: {code_submission.get('topic', 'Не указано')}

Код кандидата:
```python
{code_submission.get('user_code', '')}
```

Результаты тестов: {code_submission.get('test_results', 'Не указано')}

Проанализируй код и результаты тестов. Дай фидбэк по коду, укажи что хорошо, что можно улучшить. Если тесты не прошли, объясни почему. Оцени код от 0 до 100.

Используй тип `new_step` с полями:
- `feedback`: обратная связь по коду (2 предложения)
- `answerText`: краткий комментарий (1-2 предложения)
- `score`: оценка от 0 до 100
- `nextStep`: следующий шаг (DIALOG или CODE_TASK)"""
            
            messages = self._get_messages_with_history(input_prompt)
            response = self.llm.invoke(messages)
            ai_response = response.content if hasattr(response, 'content') else str(response)
            if not ai_response:
                raise RuntimeError("Пустой ответ от модели")
            
            parsed = self._parse_ai_response(ai_response)
            response_type = parsed.get("type", "dialog_response")
            
            self.conversation_history.append(HumanMessage(content=user_answer))
            self.conversation_history.append(AIMessage(content=ai_response))
            
            if response_type == "new_step":
                self.questions_asked += 1
                next_step = parsed.get("nextStep", {})
                next_step_type = next_step.get("type", InterviewStepType["DIALOG"])
                
                next_step_data = None
                if next_step_type == InterviewStepType["CODE_TASK"]:
                    code_task = next_step.get("codeTask", {})
                    next_step_data = {
                        "type": "CODE_TASK",
                        "code_task": {
                            "topic": code_task.get("topic", "Python"),
                            "difficulty": code_task.get("difficulty", "medium"),
                            "language": code_task.get("language", "python")
                        }
                    }
                else:
                    question_text = next_step.get("questionText", parsed.get("answerText", ""))
                    next_step_data = {
                        "type": "DIALOG",
                        "question_text": question_text
                    }
                
                return {
                    "type": "DIALOG",
                    "question_text": parsed.get("answerText", ""),
                    "status": "IN_PROGRESS",
                    "score": parsed.get("score"),
                    "ai_feedback": parsed.get("answerText", ""),
                    "user_answer": user_answer,
                    "feedback": parsed.get("feedback", ""),
                    "next_step": next_step_data
                }
            else:
                answer_text = parsed.get("answerText", "")
                return {
                    "type": "DIALOG",
                    "question_text": answer_text,
                    "status": "IN_PROGRESS",
                    "score": None,
                    "ai_feedback": answer_text,
                    "user_answer": user_answer,
                    "feedback": None,
                    "next_step": {
                        "type": "DIALOG",
                        "question_text": answer_text
                    }
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
        current_step_index = self.questions_asked
        is_last_step = (current_step_index + 1) >= self.amount_of_tasks
        
        context_info = f"Текущий шаг: статус IN_PROGRESS, индекс: {current_step_index + 1}/{self.amount_of_tasks}. Отрицательных ответов подряд: {self.negative_answers_count}."
        
        if is_negative_answer:
            warning_text = ""
            if is_last_step or should_end:
                warning_text = "\n\nВНИМАНИЕ: Это последний шаг или кандидат не знает ответы на несколько вопросов подряд. Если это последний шаг - используй `dialog_response` с вопросом 'У вас остались вопросы? Если нет - можем завершить интервью.' Если кандидат подтвердит завершение - используй `final_feedback`."
            
            input_prompt = f"""{context_info}

Кандидат ответил на твой вопрос следующим образом: '{user_answer}'.

КРИТИЧЕСКИ ВАЖНО: Кандидат сказал, что НЕ ЗНАЕТ/НЕ ИСПОЛЬЗОВАЛ/НЕ РАБОТАЛ. Это означает:
- Кандидат НЕ упомянул никаких технических деталей
- Кандидат НЕ дал правильного ответа
- Кандидат НЕ показал знаний по этой теме

ТВОЯ ЗАДАЧА:
- Используй тип `new_step` с низким score (0-30)
- В `feedback` честно укажи, что кандидат не знает ответа
- В `answerText` кратко признай это
- В `nextStep` задай следующий вопрос (DIALOG) или переходи к другой теме
- НЕ придумывай, что кандидат мог сказать
- НЕ хвали кандидата за ответ, которого он не дал
{warning_text}"""
        else:
            is_completion_confirmation = any(phrase in user_answer_lower for phrase in [
                "нет вопросов", "нет", "можно завершать", "можно завершить",
                "завершаем", "завершить", "готов", "всё", "все"
            ]) and len(user_answer_lower) < 50
            
            if self.waiting_for_completion_confirmation:
                if is_completion_confirmation:
                    input_prompt = f"""{context_info}

Кандидат подтвердил завершение интервью: '{user_answer}'.

ТВОЯ ЗАДАЧА:
- Используй тип `final_feedback`
- Предоставь итоговую обратную связь по всему интервью
- Включи оценку по каждому навыку, сильные стороны, области для улучшения"""
                else:
                    input_prompt = f"""{context_info}

Кандидат задал вопрос: '{user_answer}'.

ТВОЯ ЗАДАЧА:
- Используй тип `dialog_response`
- Ответь на вопрос кандидата
- Затем снова спроси: 'Ещё вопросы? Если нет — можем завершить.'"""
            elif is_last_step:
                input_prompt = f"""{context_info}

Кандидат ответил на твой предыдущий вопрос следующим образом: '{user_answer}'.

ТВОЯ ЗАДАЧА:
- Используй тип `new_step` для завершения последнего шага
- После этого используй `dialog_response` с вопросом 'У вас остались вопросы? Если нет — можем завершить интервью.'"""
            else:
                input_prompt = f"""{context_info}

Кандидат ответил на твой предыдущий вопрос следующим образом: '{user_answer}'.

ТВОЯ ЗАДАЧА:
- Используй тип `new_step`
- В `feedback` дай обратную связь по ответу (2 предложения)
- В `answerText` кратко прокомментируй ответ (1-2 предложения)
- В `score` оцени ответ от 0 до 100
- В `nextStep` задай следующий вопрос (DIALOG) или задачу на код (CODE_TASK)"""
        
        messages = self._get_messages_with_history(input_prompt)
        response = self.llm.invoke(messages)
        ai_response = response.content if hasattr(response, 'content') else str(response)
        if not ai_response:
            raise RuntimeError("Пустой ответ от модели")
        
        parsed = self._parse_ai_response(ai_response)
        response_type = parsed.get("type", "dialog_response")
        
        self.conversation_history.append(HumanMessage(content=user_answer))
        self.conversation_history.append(AIMessage(content=ai_response))
        
        if response_type == "final_feedback":
            self.interview_ended = True
            self.waiting_for_completion_confirmation = False
            return {
                "type": "DIALOG",
                "question_text": parsed.get("answerText", ""),
                "status": "COMPLETED",
                "score": parsed.get("totalScore"),
                "ai_feedback": parsed.get("overallFeedback", ""),
                "user_answer": user_answer,
                "feedback": parsed.get("feedback", ""),
                "next_step": None
            }
        elif response_type == "new_step":
            self.questions_asked += 1
            self.waiting_for_completion_confirmation = False
            
            next_step = parsed.get("nextStep", {})
            next_step_type = next_step.get("type", InterviewStepType["DIALOG"])
            
            next_step_data = None
            if next_step_type == InterviewStepType["CODE_TASK"]:
                code_task = next_step.get("codeTask", {})
                next_step_data = {
                    "type": "CODE_TASK",
                    "code_task": {
                        "topic": code_task.get("topic", "Python"),
                        "difficulty": code_task.get("difficulty", "medium"),
                        "language": code_task.get("language", "python")
                    }
                }
                question_text = None
            else:
                question_text = next_step.get("questionText", parsed.get("answerText", ""))
                next_step_data = {
                    "type": "DIALOG",
                    "question_text": question_text
                }
            
            if is_last_step and not self.waiting_for_completion_confirmation:
                self.waiting_for_completion_confirmation = True
            
            result = {
                "type": "DIALOG" if next_step_type == InterviewStepType["DIALOG"] else "CODE_TASK",
                "question_text": question_text,
                "status": "COMPLETED" if self.interview_ended else "IN_PROGRESS",
                "score": parsed.get("score"),
                "ai_feedback": parsed.get("answerText", ""),
                "user_answer": user_answer,
                "feedback": parsed.get("feedback", ""),
                "next_step": next_step_data
            }
            return result
        else:
            answer_text = parsed.get("answerText", "")
            
            if "остались вопросы" in answer_text.lower() or "ещё вопросы" in answer_text.lower():
                self.waiting_for_completion_confirmation = True
            
            return {
                "type": "DIALOG",
                "question_text": answer_text,
                "status": "COMPLETED" if self.interview_ended else "IN_PROGRESS",
                "score": None,
                "ai_feedback": answer_text,
                "user_answer": user_answer,
                "feedback": None,
                "next_step": {
                    "type": "DIALOG",
                    "question_text": answer_text
                }
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

    def generate_code_task(
        self,
        topic: str,
        difficulty: str,
        language: str,
    ) -> dict[str, Any]:
        """Генерация полной задачи на код по параметрам."""
        prompt = f"""Сгенерируй задачу на программирование.

Требования:
- Тема: {topic}
- Сложность: {difficulty}
- Язык: {language}

Формат ответа (JSON в ```json ... ```):
{{
  "description": "Подробное описание задачи (2-3 предложения)",
  "initial_code": "class Solution(object):\\n    def solve(self, ...):\\n        :type ...\\n        :rtype ...\\n        pass",
  "test_cases": [
    {{"input": "...", "output": "..."}},
    {{"input": "...", "output": "..."}},
    {{"input": "...", "output": "..."}}
  ],
  "topic": "{topic}",
  "difficulty": "{difficulty}",
  "language": "{language}"
}}

ВАЖНО:
- initial_code должен быть в формате класса Solution с методом solve (как на LeetCode)
- test_cases: массив из 2-3 тестов, каждый с полями "input" и "output"
- input и output - строки, которые можно использовать для тестирования
- description должна быть понятной и конкретной"""
        
        messages = [
            SystemMessage(content="Ты помощник для генерации задач на программирование. Всегда возвращай валидный JSON в ```json ... ```."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        parsed = self._extract_json(response_text)
        if not parsed:
            raise RuntimeError(f"Не удалось извлечь JSON из ответа модели: {response_text[:200]}")
        
        if not parsed.get("description") or not parsed.get("test_cases"):
            raise RuntimeError("Модель не вернула полную задачу")
        
        test_cases = parsed.get("test_cases", [])
        if len(test_cases) > 3:
            test_cases = test_cases[:3]
        
        return {
            "description": parsed.get("description", ""),
            "initial_code": parsed.get("initial_code", ""),
            "test_cases": test_cases,
            "topic": topic,
            "difficulty": difficulty,
            "language": language
        }

    def reset(self):
        """Сброс истории разговора."""
        self.conversation_history = []
        self.interview_ended = False
        self.code_submit_count = {}
        self.questions_asked = 0
        self.negative_answers_count = 0
