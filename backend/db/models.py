from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    JSON,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from db.session import Base


class InterviewStatus(str, enum.Enum):
    """Статус интервью."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class InterviewStepType(str, enum.Enum):
    """Тип шага интервью."""

    DIALOG = "DIALOG"
    CODE_TASK = "CODE_TASK"


class InterviewStepStatus(str, enum.Enum):
    """Статус шага интервью."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class CodeTestResultStatus(str, enum.Enum):
    """Статус результата теста кода."""

    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"


class MessageSender(str, enum.Enum):
    """Отправитель сообщения."""

    USER = "USER"
    AI = "AI"


class User(Base):
    """Модель пользователя."""

    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[str] = mapped_column(String)
    password_hash: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    interviews: Mapped[list["Interview"]] = relationship(
        "Interview",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Interview(Base):
    """Модель интервью."""

    __tablename__ = "interview"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
    )
    job_role_description: Mapped[str] = mapped_column(Text)
    amount_of_tasks: Mapped[int] = mapped_column(Integer)
    current_step_index: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[InterviewStatus] = mapped_column(
        SQLEnum(InterviewStatus),
        default=InterviewStatus.PENDING,
    )
    total_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped["User"] = relationship("User", back_populates="interviews")
    steps: Mapped[list["InterviewStep"]] = relationship(
        "InterviewStep",
        back_populates="interview",
        cascade="all, delete-orphan",
        order_by="InterviewStep.created_at",
    )
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="interview",
        cascade="all, delete-orphan",
        order_by="ChatMessage.timestamp",
    )


class CodeTask(Base):
    """Модель кодовой задачи."""

    __tablename__ = "codetask"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    description: Mapped[str] = mapped_column(Text)
    initial_code: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String)
    test_cases: Mapped[dict] = mapped_column(JSON)

    interview_steps: Mapped[list["InterviewStep"]] = relationship(
        "InterviewStep",
        back_populates="code_task",
    )


class InterviewStep(Base):
    """Модель шага интервью."""

    __tablename__ = "interviewstep"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    interview_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview.id", ondelete="CASCADE"),
        index=True,
    )
    type: Mapped[InterviewStepType] = mapped_column(SQLEnum(InterviewStepType))
    status: Mapped[InterviewStepStatus] = mapped_column(
        SQLEnum(InterviewStepStatus),
        default=InterviewStepStatus.PENDING,
    )
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ai_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    question_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    code_task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("codetask.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    code_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    code_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    interview: Mapped["Interview"] = relationship(
        "Interview",
        back_populates="steps",
    )
    code_task: Mapped["CodeTask | None"] = relationship(
        "CodeTask",
        back_populates="interview_steps",
    )
    code_test_results: Mapped[list["CodeTestResult"]] = relationship(
        "CodeTestResult",
        back_populates="interview_step",
        cascade="all, delete-orphan",
    )


class CodeTestResult(Base):
    """Модель результата теста кода."""

    __tablename__ = "codetestresult"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    interview_step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interviewstep.id", ondelete="CASCADE"),
        index=True,
    )
    test_id: Mapped[str] = mapped_column(String)
    status: Mapped[CodeTestResultStatus] = mapped_column(
        SQLEnum(CodeTestResultStatus),
    )
    details: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    interview_step: Mapped["InterviewStep"] = relationship(
        "InterviewStep",
        back_populates="code_test_results",
    )


class ChatMessage(Base):
    """Модель сообщения чата."""

    __tablename__ = "chatmessage"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    interview_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview.id", ondelete="CASCADE"),
        index=True,
    )
    sender: Mapped[MessageSender] = mapped_column(SQLEnum(MessageSender))
    text: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    interview: Mapped["Interview"] = relationship(
        "Interview",
        back_populates="chat_messages",
    )
