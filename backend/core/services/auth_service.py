from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from core.dto.auth import LoginSchema, RegisterSchema, TokenSchema
from core.dto.user import BaseUserSchema
from core.services.base import BaseDbModelService
from infrastructure.database.models.models import User
from infrastructure.errors.auth import ForbiddenException, InvalidCredentials
from infrastructure.errors.base import BadRequestException
from core.config.config import settings

import jwt
from passlib.context import CryptContext


class AuthService(BaseDbModelService[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    def _hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def _create_access_token(self, user: User) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_TIME)
        to_encode = {"sub": str(user.id), "exp": expire}
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    def _create_refresh_token(self, user: User) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_TIME)
        to_encode = {"sub": str(user.id), "exp": expire}
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    async def login_user(self, form: LoginSchema) -> TokenSchema:
        user = (
            await self.session.execute(
                select(User).where(User.email == form.email)
            )
        ).scalar_one_or_none()
        
        if not user or not self._verify_password(form.password, user.password_hash):
            raise InvalidCredentials()

        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(user)
        return TokenSchema(access_token=access_token, refresh_token=refresh_token)

    async def verify_token(self, token: str | None) -> dict:
        if not token:
            raise ForbiddenException()

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise InvalidCredentials()

    async def check_user_exist(self, token_data: dict) -> BaseUserSchema:
        try:
            user_id = UUID(token_data.get("sub"))
        except (ValueError, TypeError):
            raise InvalidCredentials()

        user = (
            await self.session.execute(
                select(User)
                .where(User.id == user_id)
            )
        ).scalar_one_or_none()
        if not user:
            raise ForbiddenException()
        return BaseUserSchema.model_validate(user, from_attributes=True)
        
    async def register_user(self, form: RegisterSchema) -> BaseUserSchema:
        existing_user = (
            await self.session.execute(
                select(User).where(User.email == form.email)
            )
        ).scalar_one_or_none()
        
        if existing_user:
            raise BadRequestException("Пользователь с таким email уже существует.")
        
        password_hash = self._hash_password(form.password)
        new_user = User(
            email=form.email,
            username=form.username,
            password_hash=password_hash,
        )
        
        self.session.add(new_user)
        await self.session.commit()
        
        access_token = self._create_access_token(new_user)
        refresh_token = self._create_refresh_token(new_user)
        return TokenSchema(access_token=access_token, refresh_token=refresh_token)
        