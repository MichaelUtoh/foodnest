from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.accounts.permissions import hasAdminPermission, hasCreateProductPermission
from app.accounts.services import get_current_user
from app.products.schemas import (
    ProductCreateSchema,
    ProductDetailSchema,
    ProductCategory,
)
from app.products.services import get_products_response
from app.core.auth import AuthHandler
from app.core._id import PyObjectId
from app.core.database import get_database
from app.core.pagination import paginate
from app.core.services import transform_mongo_data

ERROR_CODE = status.HTTP_404_NOT_FOUND
auth_handler = AuthHandler()
router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/")
async def get_products(
    category: Optional[ProductCategory] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    query = {"category": category} if category else {}
    products = await db["products"].find(query).to_list(length=None)
    cleaned = get_products_response(products)
    paginated_response = paginate(cleaned, page=page, page_size=page_size)
    return paginated_response


@router.post("", response_model=ProductDetailSchema)
async def create_product(
    product: ProductCreateSchema,
    current_user=Depends(auth_handler.auth_wrapper),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    product_in_db = await db["products"].find_one(
        {
            "name": product.name,
            "description": product.description,
            "seller_id": product.seller_id,
        }
    )
    if product_in_db:
        raise HTTPException(status_code=403, detail="Product already exists.")

    req_user = await get_current_user(current_user, db)
    if not hasCreateProductPermission(req_user):
        raise HTTPException(
            status_code=403,
            detail="Only wholesalers or admins can perform this action.",
        )

    new_product = await db["products"].insert_one(product.dict(by_alias=True))
    created_product = await db["products"].find_one({"_id": new_product.inserted_id})
    created_product = transform_mongo_data(created_product)
    return created_product


@router.patch("/{id}", response_model=ProductDetailSchema)
async def update_product(
    id: str,
    product: ProductCreateSchema,
    current_user=Depends(auth_handler.auth_wrapper),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    product_in_db = await db["products"].find_one({"_id": PyObjectId(id)})
    if not product_in_db:
        raise HTTPException(status_code=403, detail="Product not found.")

    req_user = await get_current_user(current_user, db)
    if not (
        hasAdminPermission(req_user) or req_user["_id"] == product_in_db["seller_id"]
    ):
        msg = "Only admins or product owner can perform this action."
        raise HTTPException(status_code=403, detail=msg)

    new_product = await db["products"].insert_one(product.dict(by_alias=True))
    created_product = await db["products"].find_one({"_id": new_product.inserted_id})
    created_product = transform_mongo_data(created_product)
    return created_product
