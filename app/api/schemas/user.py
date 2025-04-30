from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.db.models import UserRole


class UserBase(BaseModel):
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str


class UserLogin(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID
    role: UserRole
