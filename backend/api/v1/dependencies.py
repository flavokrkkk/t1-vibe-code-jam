from typing import Annotated, AsyncGenerator

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.dto.user import BaseUserSchema
import core.services as services


token_scheme = HTTPBearer(auto_error=False)


async def get_db_session(
    request: Request,
) -> AsyncGenerator[AsyncSession, None]:
    session = await request.app.state.db_connection.get_session()
    try:
        yield session
    finally:
        await session.close()


async def get_auth_service(session=Depends(get_db_session)) -> services.AuthService:
    return services.AuthService(
        session=session
    )


async def get_current_user_dependency(
    auth_service: Annotated[services.AuthService, Depends(get_auth_service)],
    auth_scheme: Annotated[HTTPAuthorizationCredentials | None, Depends(token_scheme)]
) -> BaseUserSchema:
    token = auth_scheme.credentials if auth_scheme else None
    token_data = await auth_service.verify_token(token)
    return await auth_service.check_user_exist(token_data)


async def get_interview_service(session=Depends(get_db_session)) -> services.InterviewService:
    return services.InterviewService(
        session=session
    )


async def get_message_service(session=Depends(get_db_session)) -> services.MessageService:
    return services.MessageService(
        session=session
    )