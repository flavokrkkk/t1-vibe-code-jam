from typing import Annotated
from fastapi import APIRouter, Depends

from infrastructure.errors.base import NotFoundException
from utils.error_extra import error_response
from core.services import InterviewService
from api.v1.dependencies import get_current_user_dependency, get_interview_service
from core.dto.interview import ListInterviewItemSchema
from core.dto.user import BaseUserSchema


router = APIRouter()


@router.get("/interviews", responses={**error_response(NotFoundException)})
async def get_user_interviews(
    current_user: Annotated[BaseUserSchema, Depends(get_current_user_dependency)],
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
) -> list[ListInterviewItemSchema]:
    return await interview_service.find_all_user_interviews(current_user.id)
