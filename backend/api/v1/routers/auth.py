from typing import Annotated
from fastapi import APIRouter, Depends

from api.v1.dependencies import get_auth_service, get_current_user_dependency
from infrastructure.errors.base import BadRequestException
from core.dto.auth import LoginSchema, RegisterSchema, TokenSchema, RefreshTokenSchema
from core.dto.user import BaseUserSchema
from core.services.auth_service import AuthService
from infrastructure.errors.auth import ForbiddenException, InvalidCredentials
from utils.error_extra import error_response


router = APIRouter()


@router.post(
    "/login",
    responses={**error_response(InvalidCredentials)}
)
async def login(
    form: LoginSchema, 
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> TokenSchema:
    return await auth_service.login_user(form)


@router.post(
    "/register",
    responses={**error_response(BadRequestException)}
)
async def register(
    form: RegisterSchema,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> TokenSchema:
    return await auth_service.register_user(form)
    

@router.get(
    "/current-user",
    responses={**error_response(ForbiddenException), **error_response(InvalidCredentials)},
)
async def current_user(
    current_user: Annotated[BaseUserSchema, Depends(get_current_user_dependency)]
) -> BaseUserSchema:
    return current_user


@router.post(
    "/refresh",
    responses={**error_response(InvalidCredentials)}
)
async def refresh_token(
    form: RefreshTokenSchema,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> TokenSchema:
    return await auth_service.refresh_token(form.refresh_token)