from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.config import settings
from core.exceptions import UnauthorizedException
from db.models import User
from db.session import AsyncSession, get_db

ph = PasswordHasher()
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Хеширование пароля."""
    return ph.hash(password)


def verify_password(hashed_password: str, password: str) -> bool:
    """Проверка пароля."""
    try:
        ph.verify(hashed_password, password)
        return True
    except VerifyMismatchError:
        return False


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Создание access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Создание refresh token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """Декодирование токена."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Токен истек")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Невалидный токен")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Получение текущего пользователя из токена."""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload.get("type") != "access":
        raise UnauthorizedException("Невалидный тип токена")
    
    user_id: str = payload.get("id")
    if user_id is None:
        raise UnauthorizedException("Токен не содержит ID пользователя")
    
    from sqlalchemy import select
    from uuid import UUID
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise UnauthorizedException("Невалидный формат ID пользователя в токене")
    
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise UnauthorizedException("Пользователь не найден")
    
    return user

