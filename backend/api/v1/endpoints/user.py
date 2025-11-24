from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_current_user
from db.models import User
from db.session import get_db
from api.v1.schemas.auth import UserResponse

router = APIRouter()


@router.get("/", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Получение информации о текущем пользователе."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
    )

