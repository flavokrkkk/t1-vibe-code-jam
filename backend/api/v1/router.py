from __future__ import annotations

from fastapi import APIRouter

from api.v1.endpoints import auth, user, interview

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(interview.router, prefix="/interviews", tags=["interviews"])

