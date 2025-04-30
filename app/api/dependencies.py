from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

from app.api.schemas.user import UserResponse
from app.db.models import UserRole
from app.errors.exceptions import ForbiddenError, UnauthorizedError, UserNotFoundError
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_token_optional(request: Request) -> str | None:
    try:
        return await oauth2_scheme(request)
    except HTTPException:
        return None


async def get_user_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> UserService:
    return UserService(uow)


async def get_auth_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> AuthService:
    return AuthService(uow)


async def get_current_user(
    token: str | None = Depends(get_token_optional),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse | None:
    if token is None:
        return None

    sub = auth_service.verify_access_token(token)

    try:
        user = await user_service.get_user_by_id(sub)
    except UserNotFoundError:
        return None

    return user


def require_user(user: UserResponse | None = Depends(get_current_user)) -> UserResponse:
    if user is None:
        raise UnauthorizedError()

    if user.role not in {UserRole.USER, UserRole.ADMIN}:
        raise ForbiddenError()

    return user


def require_admin(user: UserResponse | None = Depends(get_current_user)) -> UserResponse:
    if user is None or user.role != UserRole.ADMIN:
        raise ForbiddenError()

    return user
