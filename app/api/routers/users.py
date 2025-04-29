from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, require_admin, require_user
from app.api.schemas.user import UserFromDB

user_router = APIRouter(prefix="/api/users", tags=["User"])


@user_router.get("/me")
async def get_me(current_user: UserFromDB = Depends(require_user)):
    return {
        "message": f"Hi, id={current_user.id}, email={current_user.email}, role={current_user.role}"
    }


@user_router.get("/admin")
async def get_me_admin(current_user: UserFromDB = Depends(require_admin)):
    return {
        "message": f"Hi, admin! id={current_user.id}, email={current_user.email}, role={current_user.role}"
    }


@user_router.get("/public")
async def get_me(current_user: UserFromDB | None = Depends(get_current_user)):
    if current_user is None:
        return {"message": "no user"}
    return {
        "message": f"Hi, id={current_user.id}, email={current_user.email}, role={current_user.role}"
    }
