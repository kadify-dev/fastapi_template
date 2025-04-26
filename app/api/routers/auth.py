from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.api.dependencies import get_auth_service, get_current_user
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
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
        )
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)
    return {"access_token": access_token, "refresh_token": refresh_token}


@auth_router.post("/refresh")
async def refresh_access_token(
    refresh_token: RefreshToken, auth_service: AuthService = Depends(get_auth_service)
):
    user_id = auth_service.verify_refresh_token(refresh_token.token)
    if not user_id:
        return {"message": "токен невалидный"}
    access_token = auth_service.create_access_token(user_id)
    return {"access_token": access_token}


@auth_router.get("/me")
async def get_me(current_user: UserFromDB = Depends(get_current_user)):
    return {"message": f"Hi, id={current_user.id}, email={current_user.email}"}
