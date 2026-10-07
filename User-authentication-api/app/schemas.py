from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class Role(str, Enum):
    ADMIN = "Admin"
    USER = "User"


class UserCreate(BaseModel):
    full_name: str = Field(min_length=1)
    email: EmailStr
    phone_number: str | None = None
    password: str = Field(min_length=8)
    role: Role = Role.USER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: str = Field(min_length=1)
    email: EmailStr
    phone_number: str | None = None
    role: Role


class PasswordUpdate(BaseModel):
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    phone_number: str | None
    role: Role
    created_date: datetime