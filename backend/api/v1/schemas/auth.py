from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterSchema(BaseModel):
    """Схема регистрации."""

    email: EmailStr
    password: str = Field(..., min_length=6, description="Пароль должен быть не менее 6 символов")
    username: str = Field(..., min_length=1)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Пароль не должен быть меньше 6 символов")
        return v


class LoginSchema(BaseModel):
    """Схема входа."""

    email: EmailStr
    password: str = Field(..., min_length=6)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Пароль не должен быть меньше 6 символов")
        return v


class RefreshTokenSchema(BaseModel):
    """Схема обновления токена."""

    refresh_token: str


class TokenResponse(BaseModel):
    """Ответ с токенами."""

    access_token: str
    refresh_token: str


class UserResponse(BaseModel):
    """Ответ с данными пользователя."""

    id: str
    email: str
    username: str

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Ответ аутентификации."""

    user: UserResponse
    access_token: str
    refresh_token: str

