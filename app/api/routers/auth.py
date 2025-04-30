from fastapi import APIRouter, Depends

from app.api.dependencies import get_auth_service
from app.api.schemas.auth import AccessTokenResponse, RefreshTokenRequest, TokenPair
from app.api.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService

auth_router = APIRouter(prefix="/api/auth", tags=["Auth"])


@auth_router.post("/register")
async def register(
    user: UserCreate, auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    return await auth_service.register(user)


@auth_router.post("/login")
async def login(
    credentials: UserLogin, auth_service: AuthService = Depends(get_auth_service)
) -> TokenPair:
    return await auth_service.login(credentials)


@auth_router.post("/refresh")
async def refresh_access_token(
    refresh_token: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AccessTokenResponse:
    return await auth_service.refresh(refresh_token)
