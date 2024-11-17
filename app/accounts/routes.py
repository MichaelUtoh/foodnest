from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.auth import AuthHandler
from app.core._id import PyObjectId
from app.core.database import get_database
from app.accounts.schemas import (
    UserLoginResponseSchema,
    UserLoginSchema,
    UserRegisterSchema,
    UserUpdateSchema,
    UserInfoResponseSchema,
)
from app.accounts.services import get_current_user

ERROR_CODE = status.HTTP_404_NOT_FOUND
auth_handler = AuthHandler()
router = APIRouter(prefix="/auth/user")


@router.post(
    "/login",
    response_model=UserLoginResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def login(
    user: UserLoginSchema, db: AsyncIOMotorDatabase = Depends(get_database)
):
    existing_user = await db["users"].find_one({"email": user.email})
    last_login_data = {"last_login": datetime.now()}
    await db["users"].update_one({"email": user.email}, {"$set": last_login_data})

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )

    if not auth_handler.verify_password(user.password, existing_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )

    return {
        "id": str(existing_user["_id"]),
        "email": existing_user["email"],
        "access_token": auth_handler.encode_token(user.email),
        "refresh_token": auth_handler.encode_refresh_token(user.email),
    }


@router.post(
    "/register",
    response_model=UserLoginResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: UserRegisterSchema, db: AsyncIOMotorDatabase = Depends(get_database)
):
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    user_dict = user.dict()
    user_dict["password"] = auth_handler.get_password_hash(user.password)
    user_dict["created_at"] = user_dict["updated_at"] = datetime.now()
    res = await db["users"].insert_one(user_dict)
    new_user = await db["users"].find_one({"_id": res.inserted_id})

    return {
        "email": user.email,
        "access_token": auth_handler.encode_token(new_user["email"]),
        "refresh_token": auth_handler.encode_refresh_token(new_user["email"]),
    }


@router.get("/{id}", response_model=UserInfoResponseSchema)
async def get_user(id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    user = await db["users"].find_one({"_id": PyObjectId(id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user["id"] = str(user["_id"])
    return user


@router.patch("/{id}", response_model=UserInfoResponseSchema)
async def update_user(
    id: str, payload: UserUpdateSchema, db: AsyncIOMotorDatabase = Depends(get_database)
):
    user = await db["users"].find_one({"_id": PyObjectId(id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    payload = payload.dict(exclude_unset=True)
    payload["updated_at"] = datetime.now()
    await db["users"].update_one({"_id": PyObjectId(id)}, {"$set": payload})
    updated_user = await db["users"].find_one({"_id": PyObjectId(id)})
    updated_user["id"] = str(updated_user["_id"])
    return updated_user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user=Depends(auth_handler.auth_wrapper),
):
    req_user = await get_current_user(current_user, db)
    user = await db["users"].find_one({"_id": PyObjectId(id)})

    if not user:
        raise HTTPException(status_code=ERROR_CODE, detail="User not found")

    if not req_user["is_admin"]:
        raise HTTPException(status_code=ERROR_CODE, detail="Not allowed, contact admin")

    await db["users"].delete_one({"_id": PyObjectId(id)})
