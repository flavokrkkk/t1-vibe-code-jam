from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterSchema(BaseModel):
    """Схема регистрации."""

    email: EmailStr
    password: str = Field(..., min_length=6, description="Пароль должен быть не менее 6 символов")
    username: str = Field(..., min_length=1)


class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
