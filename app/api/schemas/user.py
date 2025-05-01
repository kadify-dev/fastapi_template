import re
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.db.models import UserRole


_PASSWORD_LETTER_PATTERN = re.compile(r"[a-zA-Z]")
_PASSWORD_DIGIT_PATTERN = re.compile(r"\d")
_PASSWORD_FORBIDDEN_CHARS_PATTERN = re.compile(r"[\s'\"\\]")


class UserBase(BaseModel):
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=64)

    @field_validator("password")
    def validate_password(cls, v):
        if not _PASSWORD_LETTER_PATTERN.search(v) or not _PASSWORD_DIGIT_PATTERN.search(v):
            raise ValueError("Password must contain both letters and numbers")

        if _PASSWORD_FORBIDDEN_CHARS_PATTERN.search(v):
            raise ValueError("Password cannot contain spaces, quotes or backslashes")

        return v

    @field_validator("email")
    def validate_email(cls, v):
        return v.lower().strip()


class UserLogin(UserBase):
    password: str = Field(..., min_length=8, max_length=64)


class UserResponse(UserBase):
    id: UUID
    role: UserRole
