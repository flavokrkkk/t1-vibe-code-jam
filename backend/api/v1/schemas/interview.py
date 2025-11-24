from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


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


class CodeTestResultResponse(BaseModel):
    """Схема результата теста кода."""

    id: UUID
    test_id: str
    status: str
    details: str | None

    class Config:
        from_attributes = True


class CodeTaskResponse(BaseModel):
    """Схема кодовой задачи."""

    id: UUID
    description: str
    initial_code: str
    language: str
    test_cases: dict[str, Any]

    class Config:
        from_attributes = True


class InterviewStepResponse(BaseModel):
    """Схема шага интервью."""

    id: UUID
    type: str
    status: str
    score: int | None
    ai_feedback: str | None
    question_text: str | None
    user_answer: str | None
    feedback: str | None
    code_task_id: UUID | None
    user_code: str | None
    code_feedback: str | None
    code_score: int | None
    created_at: datetime
    code_task: CodeTaskResponse | None = None
    code_test_results: list[CodeTestResultResponse] = []

    class Config:
        from_attributes = True


class ChatMessageResponse(BaseModel):
    """Схема сообщения чата."""

    id: UUID
    sender: str
    text: str
    timestamp: datetime

    class Config:
        from_attributes = True


class InterviewResponse(BaseModel):
    """Схема интервью."""

    id: UUID
    user_id: UUID
    job_role_description: str
    amount_of_tasks: int
    key_skills: list[str] = []
    preferences: str | None = None
    current_step_index: int
    status: str
    total_score: int | None
    overall_feedback: str | None
    created_at: datetime
    updated_at: datetime
    steps: list[InterviewStepResponse] = []
    chat_messages: list[ChatMessageResponse] = []

    class Config:
        from_attributes = True
