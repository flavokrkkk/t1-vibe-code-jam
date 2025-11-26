from __future__ import annotations

from fastapi import APIRouter, Depends

from api.v1.routers.auth import router as auth_router
from api.v1.routers.user import router as user_router
from api.v1.routers.interview import router as interview_router
from api.v1.routers.code import router as code_router
from api.v1.dependencies import get_current_user_dependency

api_router = APIRouter(prefix="/api/v1")
PROTECTED = Depends(get_current_user_dependency)

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(user_router, prefix="/user", tags=["user"], dependencies=[PROTECTED])
api_router.include_router(interview_router, prefix="/interviews", tags=["interviews"], dependencies=[PROTECTED])
api_router.include_router(code_router, prefix="/code", tags=["code"], dependencies=[PROTECTED])

