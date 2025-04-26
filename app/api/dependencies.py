import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_user_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> UserService:
    return UserService(uow)


async def get_auth_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> AuthService:
    return AuthService(uow)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
):
    user_id = auth_service.verify_access_token(token)
    if not user_id:
        raise credentials_exception

    user = await user_service.get_user_by_id(int(user_id))
    if not user:
        raise credentials_exception

    return user


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
