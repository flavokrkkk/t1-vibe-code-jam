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
from scibox_config import DEFAULT_CHAT_MODEL, DEFAULT_CODER_MODEL
from code_task_agent import CodeTaskAgent

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


def get_system_prompt(job_title: str, required_skills: list[str], amount_of_tasks: int, preferences: str | None = None) -> str:
    """Генерация системного промпта для интервью."""
    skills_text = ", ".join(required_skills) if required_skills else "не указаны"
    preferences_text = f"\n\n### ДОПОЛНИТЕЛЬНЫЕ ПРЕДПОЧТЕНИЯ:\n{preferences}\n\nУчитывай эти предпочтения при планировании интервью." if preferences else ""
    
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

- Используй **ТОЛЬКО** для:

  - Уточнения: "У вас остались вопросы? Если нет — можем завершить интервью." (после последнего шага, когда ждем подтверждения завершения)

- **КРИТИЧЕСКИ ВАЖНО**: 
  - Если это НЕ последний шаг — **НИКОГДА** не используй `dialog_response`
  - Если кандидат задал вопрос или ответил на твой вопрос — используй `new_step` с `nextStep.questionText` для следующего вопроса
  - `dialog_response` используй ТОЛЬКО когда уже спросил "У вас остались вопросы?" и ждешь ответа

- answerText: **1–2 предложения**, вежливо, профессионально.

```json
{{
  "type": "dialog_response",
  "answerText": "У вас остались вопросы? Если нет — можем завершить интервью."
}}
```

#### 2. new_step — завершить шаг и дать новый

- Обязательно: `answerText`, `feedback`, `score`, `nextStep`

- **feedback**: **2 предложения** — что хорошо, что можно улучшить, конкретные примеры (до 400 символов). Если длиннее — обрежь.

- **answerText**: 1–2 предложения. **НЕ ДУБЛИРУЙ feedback** — это должен быть отдельный краткий комментарий, например "Хорошо, переходим дальше" или "Понятно, давайте проверим на практике".

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

- Требуемые навыки: {skills_text}{preferences_text}

- Статус: **не завершай, пока не будет подтверждения**

### ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА ДЛЯ ВСЕХ ИНТЕРВЬЮ:

- **ОБЯЗАТЕЛЬНО должен быть минимум один шаг с типом `{InterviewStepType["CODE_TASK"]}`** в ходе интервью.

- Это правило имеет **высший приоритет** — даже если все остальные шаги диалоговые, **минимум один** должен быть кодовая задача.

- **Используй CODE_TASK активно** — если кандидат показал базовые знания, дай ему кодовую задачу для проверки практических навыков. Особенно после 2-3 диалоговых вопросов.

- **КРИТИЧЕСКИ ВАЖНО**: Если до последнего шага не было ни одной CODE_TASK, то последний шаг **ОБЯЗАТЕЛЬНО** должен быть CODE_TASK.

- **В answerText НЕ ДУБЛИРУЙ feedback** — answerText должен быть кратким комментарием (1-2 предложения), а feedback — детальным анализом. Они должны быть разными!

---

**НАЧИНАЙ ОТВЕТ СРАЗУ С ```json** и **ЗАКАНЧИВАЙ ```** — без пояснений.

### ВАЖНО ДЛЯ ПЕРВОГО ШАГА:

При начале интервью **ОБЯЗАТЕЛЬНО**:
1. Представься как интервьюер
2. Поприветствуй кандидата
3. Задай первый вопрос

**КРИТИЧЕСКИ ВАЖНО:** В `answerText` должно быть **приветствие И первый вопрос вместе** (например: "Здравствуйте! Меня зовут [имя], я буду проводить интервью на позицию {job_title}. Давайте начнем. Расскажите о вашем опыте работы с Python?").

В `nextStep.questionText` можно указать только вопрос (без приветствия), но лучше оставить его пустым или повторить только вопрос для следующего шага.

**НЕ ДУБЛИРУЙ** вопрос — если он уже есть в `answerText`, не повторяй его в `nextStep.questionText`.

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
        self.code_task_agent = CodeTaskAgent(api_key=api_key)
        self.conversation_history: list[Any] = []
        self.interview_ended = False
        self.amount_of_tasks = 0
        self.job_title = ""
        self.required_skills: list[str] = []
        self.preferences: str | None = None
        self.code_submit_count: dict[str, int] = {}
        self.questions_asked = 0
        self.negative_answers_count = 0
        self.waiting_for_completion_confirmation = False
        self.has_code_task = False

    def _get_messages_with_history(self, user_input: str) -> list:
        """Создание списка сообщений с полной историей для диалогового режима."""
        system_prompt = get_system_prompt(
            self.job_title,
            self.required_skills,
            self.amount_of_tasks,
            self.preferences
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

    def _stream_llm_response(self, messages: list) -> Any:
        """Стриминг ответа от LLM."""
        return self.llm.stream(messages)

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
        preferences: str | None = None,
    ) -> dict[str, Any]:
        """Начало интервью - получение первого вопроса в формате STEP."""
        self.job_title = job_title
        self.required_skills = required_skills
        self.amount_of_tasks = amount_of_tasks
        self.preferences = preferences
        self.interview_ended = False
        self.conversation_history = []
        self.code_submit_count = {}
        self.questions_asked = 0
        self.negative_answers_count = 0
        
        messages = [
            SystemMessage(content=get_system_prompt(
                self.job_title,
                self.required_skills,
                self.amount_of_tasks,
                self.preferences
            )),
            HumanMessage(content="Начни интервью. Обязательно представься, поприветствуй кандидата и задай первый вопрос. В answerText должно быть приветствие и первый вопрос вместе.")
        ]
        
        response = self.llm.invoke(messages)
        response_text = response.content if hasattr(response, 'content') else str(response)
        if not response_text:
            raise RuntimeError("Пустой ответ от модели")
        
        parsed = self._parse_ai_response(response_text)
        
        if parsed.get("type") == "new_step":
            next_step = parsed.get("nextStep", {})
            next_step_type = next_step.get("type", InterviewStepType["DIALOG"])
            answer_text = parsed.get("answerText", "")
            next_question_text = next_step.get("questionText", "")
            
            if self.questions_asked == 0:
                question_text = answer_text or next_question_text
            else:
                question_text = next_question_text or answer_text
            
            if not question_text:
                question_text = "Следующий вопрос." if next_step_type == InterviewStepType["DIALOG"] else "Переходим к кодовой задаче."
            
            next_step_data = None
            if next_step_type == InterviewStepType["CODE_TASK"]:
                self.has_code_task = True
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
                    "question_text": next_question_text or answer_text
                }
            
            self.conversation_history.append(HumanMessage(content="Начни интервью"))
            self.conversation_history.append(AIMessage(content=response_text))
            self.questions_asked = 1
            
            return {
                "type": "DIALOG",
                "question_text": question_text,
                "status": "IN_PROGRESS",
                "score": parsed.get("score"),
                "ai_feedback": answer_text,
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

    def start_interview_stream(
        self,
        job_title: str,
        required_skills: list[str],
        amount_of_tasks: int,
        preferences: str | None = None,
    ):
        """Начало интервью со стримингом ответа."""
        self.job_title = job_title
        self.required_skills = required_skills
        self.amount_of_tasks = amount_of_tasks
        self.preferences = preferences
        self.interview_ended = False
        self.conversation_history = []
        self.code_submit_count = {}
        self.questions_asked = 0
        self.negative_answers_count = 0
        
        messages = [
            SystemMessage(content=get_system_prompt(
                self.job_title,
                self.required_skills,
                self.amount_of_tasks,
                self.preferences
            )),
            HumanMessage(content="Начни интервью. Обязательно представься, поприветствуй кандидата и задай первый вопрос. В answerText должно быть приветствие и первый вопрос вместе.")
        ]
        
        full_response = ""
        for chunk in self._stream_llm_response(messages):
            if hasattr(chunk, 'content'):
                content = chunk.content
                if content:
                    full_response += content
                    yield content
        
        if not full_response:
            raise RuntimeError("Пустой ответ от модели")
        
        parsed = self._parse_ai_response(full_response)
        
        if parsed.get("type") == "new_step":
            next_step = parsed.get("nextStep", {})
            next_step_type = next_step.get("type", InterviewStepType["DIALOG"])
            answer_text = parsed.get("answerText", "")
            next_question_text = next_step.get("questionText", "")
            
            if self.questions_asked == 0:
                question_text = answer_text or next_question_text
            else:
                question_text = next_question_text or answer_text
            
            if not question_text:
                question_text = "Следующий вопрос." if next_step_type == InterviewStepType["DIALOG"] else "Переходим к кодовой задаче."
            
            next_step_data = None
            if next_step_type == InterviewStepType["CODE_TASK"]:
                self.has_code_task = True
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
                    "question_text": next_question_text or answer_text
                }
            
            self.conversation_history.append(HumanMessage(content="Начни интервью"))
            self.conversation_history.append(AIMessage(content=full_response))
            self.questions_asked = 1
        else:
            answer_text = parsed.get("answerText", full_response[:300])
            self.conversation_history.append(HumanMessage(content="Начни интервью"))
            self.conversation_history.append(AIMessage(content=full_response))

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
        
        # Обработка пустых ответов
        if not user_answer or not user_answer.strip():
            # Если ждем подтверждения завершения и получили пустой ответ, 
            # даем модели самой решить, что это значит
            if self.waiting_for_completion_confirmation:
                user_answer = ""  # Оставляем пустым, модель сама решит
            else:
                # Если не ждем завершения, пустой ответ - это просто пауза, 
                # не нужно на это реагировать, просто вернем текущее состояние
                return {
                    "type": "DIALOG",
                    "question_text": "Пожалуйста, введите ваш ответ.",
                    "status": "IN_PROGRESS",
                    "score": None,
                    "ai_feedback": None,
                    "user_answer": "",
                    "feedback": None,
                    "next_step": {
                        "type": "DIALOG",
                        "question_text": "Пожалуйста, введите ваш ответ."
                    }
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
                
                answer_text = parsed.get("answerText", "")
                next_question_text = next_step.get("questionText", "")
                full_code_task = None
                
                next_step_data = None
                if next_step_type == InterviewStepType["CODE_TASK"]:
                    self.has_code_task = True
                    code_task = next_step.get("codeTask", {})
                    topic = code_task.get("topic", "Python")
                    difficulty = code_task.get("difficulty", "medium")
                    language = code_task.get("language", "python")
                    
                    try:
                        full_code_task = self.generate_code_task(topic, difficulty, language)
                        question_text = answer_text or "Переходим к кодовой задаче."
                    except Exception as e:
                        logger.error(f"Ошибка генерации задачи: {e}")
                        question_text = answer_text or "Переходим к кодовой задаче."
                        full_code_task = {
                            "description": "Ошибка генерации задачи",
                            "initial_code": "",
                            "test_cases": [],
                            "topic": topic,
                            "difficulty": difficulty,
                            "language": language
                        }
                    
                    next_step_data = {
                        "type": "CODE_TASK",
                        "code_task": {
                            "topic": topic,
                            "difficulty": difficulty,
                            "language": language
                        }
                    }
                else:
                    question_text = next_question_text or answer_text
                    if not question_text:
                        question_text = "Следующий вопрос."
                    next_step_data = {
                        "type": "DIALOG",
                        "question_text": question_text
                    }
                
                result = {
                    "type": "DIALOG" if next_step_type == InterviewStepType["DIALOG"] else "CODE_TASK",
                    "question_text": question_text,
                    "status": "IN_PROGRESS",
                    "score": parsed.get("score"),
                    "ai_feedback": answer_text,
                    "user_answer": user_answer,
                    "feedback": parsed.get("feedback", ""),
                    "next_step": next_step_data
                }
                
                if full_code_task:
                    result["code_task"] = full_code_task
                
                return result
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
            if self.waiting_for_completion_confirmation:
                # Модель сама должна решить, хочет ли пользователь завершить интервью
                if not user_answer or not user_answer.strip():
                    # Пустой ответ при ожидании завершения - считаем подтверждением
                    user_answer = "нет вопросов"
                
                input_prompt = f"""{context_info}

Ты спросил кандидата: "У вас остались вопросы? Если нет — можем завершить интервью."

Кандидат ответил: '{user_answer}'

ТВОЯ ЗАДАЧА - ПРОАНАЛИЗИРУЙ ОТВЕТ И ПРИМИ РЕШЕНИЕ:
- Если кандидат явно или неявно говорит, что вопросов нет (например: "нет", "нет вопросов", "можно завершать", "давай завершим", "всё", "готово", "нет, пока", пустой ответ и т.д.) → используй тип `final_feedback`
- Если кандидат задал вопрос или хочет что-то уточнить → используй тип `new_step`, ответь на вопрос, затем снова спроси "Ещё вопросы? Если нет — можем завершить."

ВАЖНО: Анализируй смысл ответа, а не только точные слова. Если кандидат не задает вопрос, а просто отвечает на твой вопрос о завершении (включая пустой ответ) - это подтверждение завершения."""
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
        - **ОБЯЗАТЕЛЬНО** используй тип `new_step` (НЕ `dialog_response`)
        - В `feedback` дай обратную связь по ответу (2 предложения)
        - В `answerText` кратко прокомментируй ответ (1-2 предложения) — **НЕ ДУБЛИРУЙ feedback**, это должен быть отдельный краткий комментарий
        - В `score` оцени ответ от 0 до 100
        - В `nextStep` **ОБЯЗАТЕЛЬНО** задай следующий вопрос (DIALOG с questionText) или задачу на код (CODE_TASK)
        - **КРИТИЧЕСКИ ВАЖНО**: Всегда должен быть следующий вопрос или задача, интервью не должно останавливаться
        - **ВАЖНО**: Если это позиция developer и прошло уже 2-3 диалоговых вопроса, используй CODE_TASK для проверки практических навыков"""
        
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
            
            answer_text = parsed.get("answerText", "")
            next_question_text = next_step.get("questionText", "")
            
            next_step_data = None
            full_code_task = None
            
            if next_step_type == InterviewStepType["CODE_TASK"]:
                self.has_code_task = True
                code_task = next_step.get("codeTask", {})
                topic = code_task.get("topic", "Python")
                difficulty = code_task.get("difficulty", "medium")
                language = code_task.get("language", "python")
                
                try:
                    full_code_task = self.generate_code_task(topic, difficulty, language)
                    question_text = f"{answer_text or 'Переходим к кодовой задаче.'}\n\n**Задача:**\n{full_code_task['description']}\n\n**Начальный код:**\n```{language}\n{full_code_task['initial_code']}\n```"
                except Exception as e:
                    logger.error(f"Ошибка генерации задачи: {e}")
                    question_text = answer_text or "Переходим к кодовой задаче."
                    full_code_task = {
                        "description": "Ошибка генерации задачи",
                        "initial_code": "",
                        "test_cases": [],
                        "topic": topic,
                        "difficulty": difficulty,
                        "language": language
                    }
                
                next_step_data = {
                    "type": "CODE_TASK",
                    "code_task": {
                        "topic": topic,
                        "difficulty": difficulty,
                        "language": language
                    }
                }
            else:
                question_text = next_question_text or answer_text
                if not question_text:
                    question_text = "Следующий вопрос."
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
            
            if full_code_task:
                result["code_task"] = full_code_task
            
            return result
        else:
            # dialog_response - нужно задать следующий вопрос, если это не последний шаг
            answer_text = parsed.get("answerText", "")
            
            if "остались вопросы" in answer_text.lower() or "ещё вопросы" in answer_text.lower():
                self.waiting_for_completion_confirmation = True
                next_question_text = answer_text
            elif is_last_step and not self.waiting_for_completion_confirmation:
                # Если это последний шаг, но еще не спрашивали про завершение
                next_question_text = answer_text + "\n\nУ вас остались вопросы? Если нет — можем завершить интервью."
                self.waiting_for_completion_confirmation = True
            else:
                # Нужно задать следующий вопрос - запрашиваем у модели
                if not self.waiting_for_completion_confirmation:
                    follow_up_prompt = f"""{context_info}

Ты только что ответил на вопрос кандидата: '{answer_text}'.

ТВОЯ ЗАДАЧА:
- Используй тип `new_step` для завершения текущего шага
- В `answerText` кратко прокомментируй ответ кандидата (1-2 предложения)
- В `feedback` дай обратную связь по ответу (2 предложения)
- В `score` оцени ответ от 0 до 100
- В `nextStep` задай следующий вопрос (DIALOG) или задачу на код (CODE_TASK)"""
                    
                    follow_up_messages = self._get_messages_with_history(follow_up_prompt)
                    follow_up_response = self.llm.invoke(follow_up_messages)
                    follow_up_text = follow_up_response.content if hasattr(follow_up_response, 'content') else str(follow_up_response)
                    
                    if follow_up_text:
                        follow_up_parsed = self._parse_ai_response(follow_up_text)
                        if follow_up_parsed.get("type") == "new_step":
                            self.questions_asked += 1
                            follow_up_next_step = follow_up_parsed.get("nextStep", {})
                            follow_up_next_step_type = follow_up_next_step.get("type", InterviewStepType["DIALOG"])
                            
                            follow_up_answer_text = follow_up_parsed.get("answerText", "")
                            follow_up_next_question_text = follow_up_next_step.get("questionText", "")
                            
                            full_code_task = None
                            if follow_up_next_step_type == InterviewStepType["CODE_TASK"]:
                                self.has_code_task = True
                                code_task = follow_up_next_step.get("codeTask", {})
                                topic = code_task.get("topic", "Python")
                                difficulty = code_task.get("difficulty", "medium")
                                language = code_task.get("language", "python")
                                
                                try:
                                    full_code_task = self.generate_code_task(topic, difficulty, language)
                                    next_question_text = follow_up_answer_text or "Переходим к кодовой задаче."
                                except Exception as e:
                                    logger.error(f"Ошибка генерации задачи: {e}")
                                    next_question_text = follow_up_answer_text or "Переходим к кодовой задаче."
                                    full_code_task = {
                                        "description": "Ошибка генерации задачи",
                                        "initial_code": "",
                                        "test_cases": [],
                                        "topic": topic,
                                        "difficulty": difficulty,
                                        "language": language
                                    }
                                
                                next_step_data = {
                                    "type": "CODE_TASK",
                                    "code_task": {
                                        "topic": topic,
                                        "difficulty": difficulty,
                                        "language": language
                                    }
                                }
                            else:
                                next_question_text = follow_up_next_question_text or follow_up_answer_text
                                if not next_question_text:
                                    next_question_text = "Следующий вопрос."
                                next_step_data = {
                                    "type": "DIALOG",
                                    "question_text": next_question_text
                                }
                            
                            self.conversation_history.append(AIMessage(content=follow_up_text))
                            
                            result = {
                                "type": "DIALOG" if follow_up_next_step_type == InterviewStepType["DIALOG"] else "CODE_TASK",
                                "question_text": next_question_text,
                                "status": "COMPLETED" if self.interview_ended else "IN_PROGRESS",
                                "score": follow_up_parsed.get("score"),
                                "ai_feedback": follow_up_answer_text,
                                "user_answer": user_answer,
                                "feedback": follow_up_parsed.get("feedback", ""),
                                "next_step": next_step_data
                            }
                            
                            if full_code_task:
                                result["code_task"] = full_code_task
                            
                            return result
                
                # Если не удалось сгенерировать следующий вопрос, используем ответ как вопрос
                next_question_text = answer_text
            
            return {
                "type": "DIALOG",
                "question_text": next_question_text,
                "status": "COMPLETED" if self.interview_ended else "IN_PROGRESS",
                "score": None,
                "ai_feedback": answer_text,
                "user_answer": user_answer,
                "feedback": None,
                "next_step": {
                    "type": "DIALOG",
                    "question_text": next_question_text
                }
            }

    def process_answer_stream(self, user_answer: str):
        """Обработка ответа кандидата со стримингом."""
        if self.interview_ended:
            yield json.dumps({
                "type": "DIALOG",
                "question_text": "Интервью уже завершено.",
                "status": "COMPLETED",
                "score": None,
                "ai_feedback": None,
                "user_answer": user_answer,
                "feedback": None,
                "next_step": None
            })
            return
        
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
            full_response = ""
            for chunk in self._stream_llm_response(messages):
                if hasattr(chunk, 'content'):
                    content = chunk.content
                    if content:
                        full_response += content
                        yield content
            
            if not full_response:
                raise RuntimeError("Пустой ответ от модели")
            
            parsed = self._parse_ai_response(full_response)
            response_type = parsed.get("type", "dialog_response")
            
            self.conversation_history.append(HumanMessage(content=user_answer))
            self.conversation_history.append(AIMessage(content=full_response))
            return
        
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
            if self.waiting_for_completion_confirmation:
                # Модель сама должна решить, хочет ли пользователь завершить интервью
                if not user_answer or not user_answer.strip():
                    # Пустой ответ при ожидании завершения - считаем подтверждением
                    user_answer = "нет вопросов"
                
                input_prompt = f"""{context_info}

Ты спросил кандидата: "У вас остались вопросы? Если нет — можем завершить интервью."

Кандидат ответил: '{user_answer}'

ТВОЯ ЗАДАЧА - ПРОАНАЛИЗИРУЙ ОТВЕТ И ПРИМИ РЕШЕНИЕ:
- Если кандидат явно или неявно говорит, что вопросов нет (например: "нет", "нет вопросов", "можно завершать", "давай завершим", "всё", "готово", "нет, пока", пустой ответ и т.д.) → используй тип `final_feedback`
- Если кандидат задал вопрос или хочет что-то уточнить → используй тип `new_step`, ответь на вопрос, затем снова спроси "Ещё вопросы? Если нет — можем завершить."

ВАЖНО: Анализируй смысл ответа, а не только точные слова. Если кандидат не задает вопрос, а просто отвечает на твой вопрос о завершении (включая пустой ответ) - это подтверждение завершения."""
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
        - **ОБЯЗАТЕЛЬНО** используй тип `new_step` (НЕ `dialog_response`)
        - В `feedback` дай обратную связь по ответу (2 предложения)
        - В `answerText` кратко прокомментируй ответ (1-2 предложения) — **НЕ ДУБЛИРУЙ feedback**, это должен быть отдельный краткий комментарий
        - В `score` оцени ответ от 0 до 100
        - В `nextStep` **ОБЯЗАТЕЛЬНО** задай следующий вопрос (DIALOG с questionText) или задачу на код (CODE_TASK)
        - **КРИТИЧЕСКИ ВАЖНО**: Всегда должен быть следующий вопрос или задача, интервью не должно останавливаться
        - **ВАЖНО**: Если это позиция developer и прошло уже 2-3 диалоговых вопроса, используй CODE_TASK для проверки практических навыков"""
        
        messages = self._get_messages_with_history(input_prompt)
        full_response = ""
        for chunk in self._stream_llm_response(messages):
            if hasattr(chunk, 'content'):
                content = chunk.content
                if content:
                    full_response += content
                    yield content
        
        if not full_response:
            raise RuntimeError("Пустой ответ от модели")
        
        parsed = self._parse_ai_response(full_response)
        response_type = parsed.get("type", "dialog_response")
        
        self.conversation_history.append(HumanMessage(content=user_answer))
        self.conversation_history.append(AIMessage(content=full_response))
        
        if response_type == "final_feedback":
            self.interview_ended = True
            self.waiting_for_completion_confirmation = False
        elif response_type == "new_step":
            self.questions_asked += 1
            self.waiting_for_completion_confirmation = False
            
            if is_last_step and not self.waiting_for_completion_confirmation:
                self.waiting_for_completion_confirmation = True
        else:
            answer_text = parsed.get("answerText", "")
            if "остались вопросы" in answer_text.lower() or "ещё вопросы" in answer_text.lower():
                self.waiting_for_completion_confirmation = True

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
        
        evaluation = self.code_task_agent.evaluate_code(
            user_code=user_code,
            task_description=task_description,
            test_results=test_results
        )
        
        code_score = evaluation.get("score", 0)
        code_feedback = evaluation.get("feedback", "")
        
        passed_count = sum(1 for r in test_results if r["status"] == "PASSED")
        total_count = len(test_results)
        status = "COMPLETED" if passed_count == total_count and total_count > 0 else "IN_PROGRESS"
        
        return {
            "type": "CODE_TASK",
            "status": status,
            "user_code": user_code,
            "code_test_results": test_results,
            "code_feedback": code_feedback,
            "code_score": code_score,
            "score": code_score,
            "ai_feedback": code_feedback
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
        """Генерация полной задачи на код по параметрам используя кодовую модель."""
        return self.code_task_agent.generate_code_task(topic, difficulty, language)

    def reset(self):
        """Сброс истории разговора."""
        self.conversation_history = []
        self.interview_ended = False
        self.code_submit_count = {}
        self.questions_asked = 0
        self.negative_answers_count = 0
