from bson import ObjectId
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.core._id import PyObjectId


class UserRole(str, Enum):
    ADMIN = "admin"
    WHOLESALER = "wholesaler"
    RETAILER = "retailer"
    DISPATCH = "dispatch"


class User(BaseModel):
    id: Optional[str] = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr = Field(..., unique=True)
    password: str
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    role: str
    is_active: bool = True
    is_admin: bool = False
    last_login: datetime = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
