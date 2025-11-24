from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import BadRequestException
from core.security import get_current_user
from db.models import MessageSender, User
from db.session import get_db
from api.v1.schemas.interview import (
    ChatMessageSchema,
    CreateInterviewSchema,
    InterviewResponse,
    SubmitCodeSchema,
)
from api.v1.services.interview_service import InterviewService

logger = logging.getLogger(__name__)

router = APIRouter()
interview_service = InterviewService()


@router.post("/", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    data: CreateInterviewSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewResponse:
    """Создание нового интервью."""
    interview = await interview_service.create_interview(
        db,
        current_user.id,
        data.job_role_description,
        data.amount_of_tasks,
    )
    return InterviewResponse.model_validate(interview)


@router.get("/", response_model=list[InterviewResponse], status_code=status.HTTP_200_OK)
async def get_all_interviews(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[InterviewResponse]:
    """Получение всех интервью пользователя."""
    interviews = await interview_service.find_all_user_interviews(db, current_user.id)
    return [InterviewResponse.model_validate(interview) for interview in interviews]


@router.get(
    "/{interview_id}", response_model=InterviewResponse, status_code=status.HTTP_200_OK
)
async def get_interview(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewResponse:
    """Получение интервью по ID."""
    interview = await interview_service.find_interview_by_id(
        db, interview_id, current_user.id
    )
    return InterviewResponse.model_validate(interview)


@router.post(
    "/{interview_id}/message",
    response_model=InterviewResponse,
    status_code=status.HTTP_200_OK,
)
async def handle_chat_message(
    interview_id: UUID,
    data: ChatMessageSchema,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewResponse:
    """Обработка сообщения чата."""
    interview = await interview_service.handle_chat_message(
        db,
        interview_id,
        MessageSender.USER,
        data.text,
    )
    return InterviewResponse.model_validate(interview)


@router.post(
    "/{interview_id}/steps/{step_id}/code",
    response_model=InterviewResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_code(
    interview_id: UUID,
    step_id: UUID,
    data: SubmitCodeSchema,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewResponse:
    """Отправка кода для шага интервью."""
    interview = await interview_service.submit_code(
        db,
        interview_id,
        step_id,
        data.user_code,
    )
    return InterviewResponse.model_validate(interview)


@router.post(
    "/{interview_id}/audio",
    response_model=InterviewResponse,
    status_code=status.HTTP_200_OK,
)
async def handle_audio_message(
    interview_id: UUID,
    audio: UploadFile = File(...),
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewResponse:
    """Обработка аудио сообщения."""
    if not audio.content_type:
        raise BadRequestException("Не указан тип контента для аудио файла.")

    audio_bytes = await audio.read()
    interview = await interview_service.handle_audio_message(
        db,
        interview_id,
        audio_bytes,
        audio.content_type,
    )
    return InterviewResponse.model_validate(interview)
