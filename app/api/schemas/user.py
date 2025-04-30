from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.db.models import UserRole


class UserBase(BaseModel):
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=64)


class UserLogin(UserBase):
    password: str = Field(..., min_length=8, max_length=64)


class UserResponse(UserBase):
    id: UUID
    role: UserRole
