from __future__ import annotations

import logging
import os
import re
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)


def get_system_prompt(job_title: str, required_skills: list[str], amount_of_tasks: int) -> str:
    """Генерация системного промпта для интервью."""
    skills_text = ", ".join(required_skills) if required_skills else "не указаны"
    
    return f"""Ты профессиональный интервьюер, проводящий техническое интервью для вакансии "{job_title}".

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

    def __init__(self, api_key: str | None = None, model: str = "llama-3.3-70b-versatile"):
        """Инициализация агента."""
        if api_key is None:
            api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError(
                "Groq API key не указан. Установите переменную окружения GROQ_API_KEY "
                "или передайте api_key при создании агента. "
                "Получить ключ: https://console.groq.com/keys"
            )
        
        self.client = ChatGroq(
            model=model,
            temperature=0.7,
            groq_api_key=api_key,
        )
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
            SystemMessage(content=system_prompt),
            HumanMessage(content="Начни интервью. Представься и задай первый вопрос кандидату."),
        ]
        
        try:
            response = self.client.invoke(messages)
            first_question = response.content
            if not first_question:
                raise RuntimeError("Пустой ответ от модели")
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                raise RuntimeError(
                    "Превышена квота API. Проверьте лимиты на "
                    "https://console.groq.com"
                ) from e
            elif "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                raise RuntimeError(
                    "Ошибка аутентификации. Проверьте правильность Groq API ключа."
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
        
        system_prompt = self.conversation_history[0]["content"]
        
        messages = [SystemMessage(content=system_prompt)]
        
        for msg in self.conversation_history[1:]:
            if msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=f"Кандидат ответил: {user_answer}. Проанализируй ответ и продолжай интервью. Можешь задать уточняющие вопросы, если нужно."))
        
        try:
            response = self.client.invoke(messages)
            ai_response = response.content
            if not ai_response:
                raise RuntimeError("Пустой ответ от модели")
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                raise RuntimeError(
                    "Превышена квота API. Проверьте лимиты на "
                    "https://console.groq.com"
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
        system_prompt = self.conversation_history[0]["content"]
        
        messages = [SystemMessage(content=system_prompt)]
        
        for msg in self.conversation_history[1:]:
            if msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
        
        messages.append(HumanMessage(
            content="Интервью завершено. Предоставь итоговую обратную связь по кандидату, включая оценку по каждому навыку, сильные стороны, области для улучшения и рекомендации."
        ))
        
        try:
            response = self.client.invoke(messages)
            feedback = response.content
            if not feedback:
                raise RuntimeError("Пустой ответ от модели")
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                raise RuntimeError(
                    "Превышена квота API. Проверьте лимиты на "
                    "https://console.groq.com"
                ) from e
            raise
        
        return feedback

    def reset(self):
        """Сброс истории разговора."""
        self.conversation_history = []
        self.interview_ended = False
        self.feedback_generated = False
