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
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column



class InterviewStatus(str, enum.Enum):

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class InterviewStepType(str, enum.Enum):

    DIALOG = "DIALOG"
    CODE_TASK = "CODE_TASK"


class InterviewStepStatus(str, enum.Enum):

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class CodeTestResultStatus(str, enum.Enum):

    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"


class MessageSender(str, enum.Enum):

    USER = "USER"
    AI = "AI"



class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[str] = mapped_column(String)
    password_hash: Mapped[str] = mapped_column(String)

    interviews: Mapped[list["Interview"]] = relationship(
        "Interview",
        foreign_keys="Interview.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Interview(Base):  

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
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    job_role_description: Mapped[str] = mapped_column(Text)
    amount_of_tasks: Mapped[int] = mapped_column(Integer)
    key_skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    preferences: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_step_index: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[InterviewStatus] = mapped_column(
        SQLEnum(InterviewStatus),
        default=InterviewStatus.PENDING,
    )
    total_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    public_token: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )
    pending_next_step: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="interviews",
    )
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
        order_by="ChatMessage.created_at",
    )


class CodeTask(Base):

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
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    difficulty: Mapped[str] = mapped_column(String, default="medium")
    topic: Mapped[str] = mapped_column(String, nullable=True)

    interview_steps: Mapped[list["InterviewStep"]] = relationship(
        "InterviewStep",
        back_populates="code_task",
    )


class InterviewStep(Base):

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

    interview_step: Mapped["InterviewStep"] = relationship(
        "InterviewStep",
        back_populates="code_test_results",
    )


class ChatMessage(Base):
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

    interview: Mapped["Interview"] = relationship(
        "Interview",
        back_populates="chat_messages",
    )
