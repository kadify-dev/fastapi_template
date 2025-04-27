from datetime import timedelta

from app.api.schemas.user import UserCreate, UserFromDB
from app.core.config import settings
from app.core.exceptions import (
    AccessTokenExpiredError,
    InvalidCredentialsError,
    RefreshTokenExpiredError,
    TokenError,
    TokenExpiredError,
    UserAlreadyExistsError,
)
from app.core.security import create_token, hash_password, verify_password, verify_token
from app.utils.unitofwork import IUnitOfWork


class AuthService:

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def register_user(self, user: UserCreate) -> UserFromDB:
        async with self.uow as uow:
            existing_user = await uow.user_repo.find_by_email(user.email)
            if existing_user:
                raise UserAlreadyExistsError()

            hashed_password = hash_password(user.password)
            user_data = {"email": user.email, "hashed_password": hashed_password}

            user_from_db = await uow.user_repo.create(user_data)
            user_to_return = UserFromDB.model_validate(user_from_db)
            await uow.commit()

            return user_to_return

    async def authenticate_user(self, user: UserCreate) -> UserFromDB:
        async with self.uow as uow:
            user_from_db = await uow.user_repo.find_by_email(user.email)
            if not user_from_db or not verify_password(
                user.password, user_from_db.hashed_password
            ):
                raise InvalidCredentialsError()

            return UserFromDB.model_validate(user_from_db)

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
    def create_access_token(user_id: int) -> str:
        return create_token(
            {"sub": str(user_id), "type": "access"},
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        return create_token(
            {"sub": str(user_id), "type": "refresh"},
            timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
        )
