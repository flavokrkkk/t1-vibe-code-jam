from fastapi import status
from infrastructure.errors.base import BaseAPIException

class UnauthorizedException(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Не авторизован"
    
    def __init__(self) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Доступ запрещен"
    
    def __init__(self) -> None:
        super().__init__(status_code=self.status_code, detail=self.detail)



class InvalidCredentials(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверные учетные данные"

    def __init__(self, detail: str = detail) -> None:
        super().__init__(status_code=self.status_code, detail=detail)
