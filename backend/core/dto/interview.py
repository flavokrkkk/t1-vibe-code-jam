from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from core.config.config import settings


class CreateInterviewSchema(BaseModel):
    """Схема создания интервью."""

    job_role_description: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Описание роли должно быть не менее 10 и не более 500 символов",
    )
    amount_of_tasks: int = Field(
        ...,
        ge=1,
        le=30,
        description="Количество задач должно быть от 1 до 30",
    )
    key_skills: list[str] = Field(
        default_factory=list,
        description="Список ключевых навыков (максимум 5)",
    )
    preferences: str | None = Field(
        default=None,
        max_length=1000,
        description="Пожелания пользователя (необязательно, максимум 1000 символов)",
    )

    @field_validator("key_skills")
    @classmethod
    def validate_key_skills(cls, v: list[str]) -> list[str]:
        """Валидация ключевых навыков."""
        if len(v) > 5:
            raise ValueError("Можно добавить максимум 5 ключевых навыков")
        for skill in v:
            if not skill or not skill.strip():
                raise ValueError("Навык не может быть пустым")
            if len(skill) > 50:
                raise ValueError("Навык не может быть длиннее 50 символов")
        return v


class ChatMessageSchema(BaseModel):
    """Схема сообщения чата."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Текст сообщения не должен превышать 1000 символов",
    )


class SubmitCodeSchema(BaseModel):
    """Схема отправки кода."""

    user_code: str = Field(
        ...,
        min_length=10,
        max_length=10000,
        description="Код должен содержать от 10 до 10000 символов",
    )


class BanForCheatingSchema(BaseModel):
    """Схема бана за читинг."""

    reasons: list[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Причины бана (от 1 до 10)",
    )

    @field_validator("reasons")
    @classmethod
    def validate_reasons(cls, v: list[str]) -> list[str]:
        """Валидация причин бана."""
        if not v:
            raise ValueError("Необходимо указать хотя бы одну причину бана")
        
        for reason in v:
            if not reason or not reason.strip():
                raise ValueError("Причина бана не может быть пустой")
            if len(reason) > 200:
                raise ValueError("Причина бана не может быть длиннее 200 символов")
        
        return v


class UpdateResultUrlSchema(BaseModel):
    """Схема обновления ссылки на результат (PDF)."""

    result_url: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="URL ссылка на PDF с результатами интервью",
    )

    @field_validator("result_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Валидация URL."""
        if not v or not v.strip():
            raise ValueError("URL не может быть пустым")
        
        # Базовая проверка что это похоже на URL
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("URL должен начинаться с http:// или https://")
        
        return v.strip()


class CodeTestResultSchema(BaseModel):
    """Схема результата теста кода."""

    id: UUID
    test_id: str
    status: str
    details: str | None


class CodeTaskSchema(BaseModel):
    """Схема кодовой задачи."""

    id: UUID
    description: str
    initial_code: str
    language: str
    test_cases: list[dict[str, Any]]


class InterviewStepSchema(BaseModel):
    """Схема шага интервью."""

    id: UUID
    type: str
    status: str
    score: int | None
    question_text: str | None
    user_answer: str | None
    feedback: str | None
    code_task_id: UUID | None
    user_code: str | None
    code_feedback: str | None
    code_score: int | None
    created_at: datetime
    code_task: CodeTaskSchema | None = None
    code_test_results: list[CodeTestResultSchema] = []


class ChatMessagesSchema(BaseModel):
    """Схема сообщения чата."""

    id: UUID
    sender: str
    text: str
    created_at: datetime


class BaseInterviewSchema(BaseModel):
    id: UUID
    user_id: UUID
    creator_id: UUID
    job_role_description: str
    status: str
    created_at: datetime
    updated_at: datetime
    amount_of_tasks: int
    key_skills: list[str] = []
    preferences: str | None = None
    current_step_index: int
    total_score: int | None
    overall_feedback: str | None
    public_token: str
    ban_reasons: list[str] | None = None
    banned_at: datetime | None = None
    result_url: str | None = None

    @field_validator("public_token")
    @classmethod
    def validate_public_token(cls, v: str) -> str:
        return f"{settings.BASE_URL}/api/v1/interview/claim/{v}"


class ListInterviewItemSchema(BaseInterviewSchema):
    steps_count: int
    chat_messages_count: int
    

class InterviewSchema(BaseInterviewSchema):
    steps: list[InterviewStepSchema] = []
    chat_messages: list[ChatMessagesSchema] = []

