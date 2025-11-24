from __future__ import annotations

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.exceptions import BadRequestException, UnauthorizedException
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from db.models import User
from db.session import get_db
from api.v1.schemas.auth import (
    AuthResponse,
    LoginSchema,
    RefreshTokenSchema,
    RegisterSchema,
    TokenResponse,
    UserResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _parse_time_string(time_str: str) -> timedelta:
    """Парсинг строки времени в timedelta."""
    if time_str.endswith("m"):
        minutes = int(time_str[:-1])
        return timedelta(minutes=minutes)
    elif time_str.endswith("h"):
        hours = int(time_str[:-1])
        return timedelta(hours=hours)
    elif time_str.endswith("d"):
        days = int(time_str[:-1])
        return timedelta(days=days)
    else:
        return timedelta(minutes=15)


@router.post(
    "/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    data: RegisterSchema,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Регистрация нового пользователя."""
    result = await db.execute(select(User).where(User.email == data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise BadRequestException("Пользователь уже существует.")

    new_user = User(
        email=data.email,
        username=data.username,
        password_hash=hash_password(data.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access_token_expires = _parse_time_string(settings.JWT_ACCESS_TOKEN_TIME)
    refresh_token_expires = _parse_time_string(settings.JWT_REFRESH_TOKEN_TIME)

    access_token = create_access_token(
        data={"id": str(new_user.id)},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        data={"id": str(new_user.id)},
        expires_delta=refresh_token_expires,
    )

    return AuthResponse(
        user=UserResponse(
            id=str(new_user.id),
            email=new_user.email,
            username=new_user.username,
        ),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def login(
    data: LoginSchema,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Вход пользователя."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedException("Пользователь не найден.")

    if not verify_password(user.password_hash, data.password):
        raise UnauthorizedException("Неверный пароль.")

    access_token_expires = _parse_time_string(settings.JWT_ACCESS_TOKEN_TIME)
    refresh_token_expires = _parse_time_string(settings.JWT_REFRESH_TOKEN_TIME)

    access_token = create_access_token(
        data={"id": str(user.id)},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        data={"id": str(user.id)},
        expires_delta=refresh_token_expires,
    )

    return AuthResponse(
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
        ),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh-token", response_model=TokenResponse, status_code=status.HTTP_200_OK
)
async def refresh_token(
    data: RefreshTokenSchema,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Обновление токена."""
    try:
        payload = decode_token(data.refresh_token)
    except Exception as e:
        raise UnauthorizedException("Невалидный токен авторизации.") from e

    if payload.get("type") != "refresh":
        raise UnauthorizedException("Невалидный тип токена")

    user_id = payload.get("id")
    if not user_id:
        raise UnauthorizedException("Токен не содержит ID пользователя")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedException("Пользователь не найден.")

    access_token_expires = _parse_time_string(settings.JWT_ACCESS_TOKEN_TIME)
    refresh_token_expires = _parse_time_string(settings.JWT_REFRESH_TOKEN_TIME)

    access_token = create_access_token(
        data={"id": str(user.id)},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        data={"id": str(user.id)},
        expires_delta=refresh_token_expires,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )
