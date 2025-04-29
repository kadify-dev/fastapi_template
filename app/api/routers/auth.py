from fastapi import APIRouter, Depends

from app.api.dependencies import get_auth_service
from app.api.schemas.auth import RefreshToken
from app.api.schemas.user import UserCreate, UserFromDB
from app.services.auth_service import AuthService

auth_router = APIRouter(prefix="/api/auth", tags=["Auth"])


@auth_router.post("/register")
async def register(
    user: UserCreate, auth_service: AuthService = Depends(get_auth_service)
) -> UserFromDB:
    return await auth_service.register_user(user)


@auth_router.post("/login")
async def login(
    user: UserCreate, auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.authenticate_user(user)
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)
    return {"access_token": access_token, "refresh_token": refresh_token}


@auth_router.post("/refresh")
async def refresh_access_token(
    refresh_token: RefreshToken, auth_service: AuthService = Depends(get_auth_service)
):
    sub = auth_service.verify_refresh_token(refresh_token.token)
    access_token = auth_service.create_access_token(sub)
    return {"access_token": access_token}
