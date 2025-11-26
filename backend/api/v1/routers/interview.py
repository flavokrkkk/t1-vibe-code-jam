from __future__ import annotations

import json
import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.dependencies import get_current_user_dependency, get_interview_service
from core.dto.interview import ChatMessageSchema, CreateInterviewSchema, InterviewSchema, SubmitCodeSchema
from core.dto.user import BaseUserSchema
from infrastructure.database.models.models import MessageSender
from utils.error_extra import error_response
from infrastructure.errors.base import BadRequestException, NotFoundException

from core.services.interview_service import InterviewService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", responses={**error_response(BadRequestException)})
async def create_interview(
    data: CreateInterviewSchema,
    current_user: Annotated[BaseUserSchema, Depends(get_current_user_dependency)],
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
) -> InterviewSchema:
    return await interview_service.create_interview(
        current_user.id,
        data.job_role_description,
        data.amount_of_tasks,
        data.key_skills,
        data.preferences,
    )


@router.get(
    "/claim/",
    responses={**error_response(NotFoundException), **error_response(BadRequestException)},
)
async def claim_interview_by_link(
    public_token: str,
    current_user: Annotated[BaseUserSchema, Depends(get_current_user_dependency)],
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
) -> InterviewSchema:
    return await interview_service.claim_interview(public_token, current_user.id)


@router.get(
    "/{interview_id}", responses={**error_response(NotFoundException)}
)
async def get_interview(
    interview_id: UUID,
    current_user: Annotated[BaseUserSchema, Depends(get_current_user_dependency)],
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
) -> InterviewSchema:
    return await interview_service.find_interview_by_id(interview_id, current_user.id)


@router.post(
    "/{interview_id}/message",
    responses={**error_response(BadRequestException)}
)
async def handle_chat_message(
    interview_id: UUID,
    data: ChatMessageSchema,
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
) -> InterviewSchema:
    return await interview_service.handle_chat_message(interview_id, MessageSender.USER, data.text)


@router.post(
    "/{interview_id}/message/stream",
    responses={**error_response(BadRequestException), **error_response(NotFoundException)}
)
async def handle_chat_message_stream(
    interview_id: UUID,
    data: ChatMessageSchema,
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
):
    """SSE стриминг ответов AI - текст появляется по мере генерации"""
    async def generate_sse():
        try:
            # Отправляем начальное событие для установки соединения
            yield f": ping\n\n"
            
            # Используем новый метод с SSE стримингом
            async for event in interview_service.handle_chat_message_stream(
                interview_id, 
                MessageSender.USER, 
                data.text
            ):
                # Добавляем явный flush через двойной перенос строки
                event_data = json.dumps(event, ensure_ascii=False)
                yield f"data: {event_data}\n\n"
                
        except BadRequestException as e:
            logger.error(f"Ошибка валидации при стриминге: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.error(f"Ошибка при стриминге сообщения: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': 'Внутренняя ошибка сервера'}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Transfer-Encoding": "chunked"
        }
    )


@router.post(
    "/{interview_id}/steps/{step_id}/code",
    responses={**error_response(NotFoundException), **error_response(BadRequestException)}
)
async def submit_code(
    interview_id: UUID,
    step_id: UUID,
    data: SubmitCodeSchema,
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
) -> InterviewSchema:
    return await interview_service.submit_code(interview_id, step_id, data.user_code)


@router.post(
    "/{interview_id}/steps/{step_id}/skip",
    responses={**error_response(NotFoundException), **error_response(BadRequestException)}
)
async def skip_step(
    interview_id: UUID,
    step_id: UUID,
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
) -> InterviewSchema:
    return await interview_service.skip_step(interview_id, step_id)


@router.post(
    "/{interview_id}/audio",
    responses={**error_response(BadRequestException), **error_response(NotFoundException)}
)
async def handle_audio_message(
    interview_id: UUID,
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
    audio: UploadFile = File(...),
) -> dict[str, str]:
    """
    Обработка аудио-сообщения. Возвращает только расшифрованный текст.
    Ответ:
    {
        "text": "<распознанный текст>"
    }
    """
    text = await interview_service.handle_audio_message(interview_id, audio)
    return {"text": text}
