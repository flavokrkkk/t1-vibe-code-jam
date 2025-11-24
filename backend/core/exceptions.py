from __future__ import annotations

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Базовое исключение API."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(BaseAPIException):
    """Ресурс не найден."""

    def __init__(self, detail: str = "Ресурс не найден") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestException(BaseAPIException):
    """Некорректный запрос."""

    def __init__(self, detail: str = "Некорректный запрос") -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(BaseAPIException):
    """Не авторизован."""

    def __init__(self, detail: str = "Не авторизован") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(BaseAPIException):
    """Доступ запрещен."""

    def __init__(self, detail: str = "Доступ запрещен") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

