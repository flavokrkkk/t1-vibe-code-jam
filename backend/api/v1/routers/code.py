from typing import Annotated

from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel

from api.v1.dependencies import get_interview_service, get_current_user_dependency
from core.services.interview_service import InterviewService
from core.dto.user import BaseUserSchema
from utils.error_extra import error_response
from infrastructure.errors.base import BadRequestException

router = APIRouter()

class RunCodeRequest(BaseModel):
    source_code: str
    language: str
    test_cases: list[dict] | None = None

@router.post(
    "/run",
    responses={**error_response(BadRequestException)}
)
async def run_code(
    data: RunCodeRequest,
    interview_service: Annotated[InterviewService, Depends(get_interview_service)],
    current_user: Annotated[BaseUserSchema, Depends(get_current_user_dependency)],
):
    """
    Run code with test cases (Playground mode).
    Does not affect interview state.
    """
    return await interview_service.run_playground_code(
        data.source_code,
        data.language,
        data.test_cases
    )


