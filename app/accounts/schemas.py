from typing import Optional
from bson import ObjectId
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.accounts.models import UserRole


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    role: str = UserRole.RETAILER
    is_active: bool = True
    is_admin: bool = False


class UserUpdateSchema(BaseModel):
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    address: Optional[str]


class UserLoginResponseSchema(BaseModel):
    id: str
    email: EmailStr
    access_token: str
    refresh_token: str


class UserInfoResponseSchema(BaseModel):
    id: str
    email: EmailStr
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True
