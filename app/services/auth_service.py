from datetime import timedelta
from uuid import UUID

from app.api.schemas.auth import AccessTokenResponse, RefreshTokenRequest, TokenPair
from app.api.schemas.user import UserCreate, UserLogin, UserResponse
from app.core.config import settings
from app.core.security import create_token, hash_password, verify_password, verify_token
from app.errors.exceptions import (
    AccessTokenExpiredError,
    InvalidCredentialsError,
    RefreshTokenExpiredError,
    TokenError,
    TokenExpiredError,
    UserAlreadyExistsError,
)
from app.utils.unitofwork import IUnitOfWork


class AuthService:

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def register(self, user: UserCreate) -> UserResponse:
        async with self.uow as uow:
            user_exists = await uow.user_repo.find_by_email(user.email)
            if user_exists:
                raise UserAlreadyExistsError()

            hashed_password = hash_password(user.password)
            new_user_data = {"email": user.email, "hashed_password": hashed_password}

            created_user = await uow.user_repo.create(new_user_data)
            user_response = UserResponse.model_validate(created_user)
            await uow.commit()

            return user_response

    async def login(self, credentials: UserLogin) -> TokenPair:
        user = await self._authenticate(credentials)

        access_token = self.create_access_token(user.id)
        refresh_token = self.create_refresh_token(user.id)

        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, refresh_token: RefreshTokenRequest) -> AccessTokenResponse:
        sub = self.verify_refresh_token(refresh_token.refresh_token)
        access_token = self.create_access_token(sub)
        return AccessTokenResponse(access_token=access_token)

    async def _authenticate(self, credentials: UserLogin) -> UserResponse:
        async with self.uow as uow:
            user = await uow.user_repo.find_by_email(credentials.email)
            if not user or not verify_password(
                credentials.password, user.hashed_password
            ):
                raise InvalidCredentialsError()
            return UserResponse.model_validate(user)

    @staticmethod
    def verify_access_token(token: str):
        try:
            return verify_token(token, token_type="access")
        except TokenExpiredError:
            raise AccessTokenExpiredError()
        except TokenError as e:
            raise InvalidCredentialsError(detail=str(e))

    @staticmethod
    def verify_refresh_token(token: str):
        try:
            return verify_token(token, token_type="refresh")
        except TokenExpiredError:
            raise RefreshTokenExpiredError()
        except TokenError as e:
            raise InvalidCredentialsError(detail=str(e))

    @staticmethod
    def create_access_token(user_id: int | UUID | str) -> str:
        return create_token(
            {"sub": str(user_id), "type": "access"},
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

    @staticmethod
    def create_refresh_token(user_id: int | UUID | str) -> str:
        return create_token(
            {"sub": str(user_id), "type": "refresh"},
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
