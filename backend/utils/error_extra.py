from fastapi import HTTPException


def error_response(exception_cls: HTTPException) -> dict:
    return {
        exception_cls.status_code: {
            "description": exception_cls.detail,
            "content": {
                "application/json": {
                    "example": {"detail": exception_cls.detail}
                }
            }
        }
    }