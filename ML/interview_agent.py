from __future__ import annotations

import logging
import os
import re
from typing import Any

from scibox_client import SciBoxClient
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


class InterviewAgent:
    """ИИ-агент для проведения интервью с инструментами."""

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_CHAT_MODEL):
        """Инициализация агента."""
        if api_key is None:
            api_key = os.getenv("SCIBOX_API_KEY")
        if not api_key:
            raise ValueError("SciBox API key обязателен. Установите SCIBOX_API_KEY или передайте api_key.")
        self.client = SciBoxClient(api_key=api_key)
        self.model_name = model
        self.conversation_history: list[dict[str, Any]] = []
        self.interview_ended = False
        self.feedback_generated = False
        self.amount_of_tasks = 0

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

    def start_interview(
        self,
        job_title: str,
        required_skills: list[str],
        amount_of_tasks: int,
    ) -> str:
        """Начало интервью - получение первого вопроса."""
        system_prompt = get_system_prompt(job_title, required_skills, amount_of_tasks)
        
        self.amount_of_tasks = amount_of_tasks
        self.interview_ended = False
        self.feedback_generated = False
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Начни интервью. Представься и задай первый вопрос кандидату."},
        ]
        
        try:
            response = self.client.chat_completion(
                messages=messages,
                model=self.model_name,
                temperature=0.7,
                top_p=0.9,
                max_tokens=512,
            )
            first_question = response.choices[0].message.content
            if not first_question:
                raise RuntimeError("Пустой ответ от модели")
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "rate limit" in error_msg.lower() or "429" in error_msg:
                raise RuntimeError(
                    "Превышена квота API. Уменьшите частоту запросов или подождите."
                ) from e
            elif "authentication" in error_msg.lower() or "api_key" in error_msg.lower() or "401" in error_msg:
                raise RuntimeError(
                    "Ошибка аутентификации. Проверьте правильность SciBox API ключа."
                ) from e
            raise
        
        self.conversation_history = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": first_question},
        ]
        
        return first_question

    def process_answer(self, user_answer: str) -> str:
        """Обработка ответа кандидата и получение следующего вопроса/комментария."""
        if self.interview_ended:
            return "Интервью уже завершено."
        
        messages = []
        
        for msg in self.conversation_history:
            if msg["role"] in ["system", "user", "assistant"]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": f"Кандидат ответил: {user_answer}. Проанализируй ответ и продолжай интервью. Можешь задать уточняющие вопросы, если нужно."})
        
        try:
            response = self.client.chat_completion(
                messages=messages,
                model=self.model_name,
                temperature=0.7,
                top_p=0.9,
                max_tokens=512,
            )
            ai_response = response.choices[0].message.content
            if not ai_response:
                raise RuntimeError("Пустой ответ от модели")
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "rate limit" in error_msg.lower() or "429" in error_msg:
                raise RuntimeError(
                    "Превышена квота API. Уменьшите частоту запросов или подождите."
                ) from e
            raise
        
        if self._check_interview_end(ai_response):
            self.interview_ended = True
            ai_response = re.sub(r'\[ЗАВЕРШЕНИЕ ИНТЕРВЬЮ\]|\[END_INTERVIEW\]', '', ai_response, flags=re.IGNORECASE).strip()
        
        self.conversation_history.append({"role": "user", "content": user_answer})
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        
        return ai_response
    
    def is_interview_complete(self) -> bool:
        """Проверка, завершено ли интервью."""
        return self.interview_ended
    
    def should_end_interview(self, response: str) -> bool:
        """Проверка, хочет ли агент завершить интервью."""
        return self.interview_ended

    def generate_feedback(self) -> str:
        """Генерация итоговой обратной связи на основе всего интервью."""
        messages = []
        
        for msg in self.conversation_history:
            if msg["role"] in ["system", "user", "assistant"]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({
            "role": "user",
            "content": "Интервью завершено. Предоставь итоговую обратную связь по кандидату, включая оценку по каждому навыку, сильные стороны, области для улучшения и рекомендации."
        })
        
        try:
            response = self.client.chat_completion(
                messages=messages,
                model=self.model_name,
                temperature=0.7,
                top_p=0.9,
                max_tokens=1024,
            )
            feedback = response.choices[0].message.content
            if not feedback:
                raise RuntimeError("Пустой ответ от модели")
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "rate limit" in error_msg.lower() or "429" in error_msg:
                raise RuntimeError(
                    "Превышена квота API. Уменьшите частоту запросов или подождите."
                ) from e
            raise
        
        return feedback

    def reset(self):
        """Сброс истории разговора."""
        self.conversation_history = []
        self.interview_ended = False
        self.feedback_generated = False
