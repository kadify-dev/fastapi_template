from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str


class UserFromDB(UserBase):
    id: UUID
