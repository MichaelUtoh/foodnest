from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.accounts.permissions import (
    hasAdminPermission,
    hasOwnerPermission,
    hasRetailerPermission,
)
from app.accounts.services import get_current_user
from app.core._id import PyObjectId
from app.core.auth import AuthHandler
from app.core.database import get_database
from app.core.pagination import paginate
from app.orders.schemas import (
    OrderCreateSchema,
    OrderDetailSchema,
    OrderItemDetail,
    OrderStatus,
)
from app.core.services import transform_mongo_data

ERROR_CODE = status.HTTP_404_NOT_FOUND
auth_handler = AuthHandler()
router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/{id}")
async def get_orders_by_id(
    id: str,
    current_user=Depends(auth_handler.auth_wrapper),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    req_user = await get_current_user(current_user, db)
    if not (hasOwnerPermission(req_user)):
        msg = "Not allowed, contact Administrator"
        raise HTTPException(status_code=403, detail=msg)

    order = await db["orders"].find_one({"_id": PyObjectId(id)})
    if hasRetailerPermission(req_user) and not req_user["_id"] == order["buyer_id"]:
        msg = "Not allowed, contact Administrator"
        raise HTTPException(status_code=403, detail=msg)

    order = transform_mongo_data(order)
    return order


@router.get("/")
async def get_my_orders(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user=Depends(auth_handler.auth_wrapper),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    req_user = await get_current_user(current_user, db)
    if not hasOwnerPermission(req_user):
        raise HTTPException(status_code=403, detail="Not allowed.")

    if hasAdminPermission(req_user):
        orders = (
            await db["orders"].find({"status": status}).to_list(length=None)
            if status
            else await db["orders"].find().to_list(length=None)
        )
        return orders

    query = {"$or": [{"buyer_id": req_user["_id"]}, {"seller_id": req_user["_id"]}]}
    if status:
        query["status"] = status

    orders = await db["orders"].find(query).to_list(length=None)
    paginated_response = paginate(
        transform_mongo_data(orders), page=page, page_size=page_size
    )
    return paginated_response


@router.post("/", response_model=List[OrderItemDetail])
async def create_order(
    payload: OrderCreateSchema,
    current_user=Depends(auth_handler.auth_wrapper),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    req_user = await get_current_user(current_user, db)
    if not hasRetailerPermission(req_user):
        msg = "Not allowed, contact Administrator"
        raise HTTPException(status_code=403, detail=msg)

    order_items = payload.dict()["items"]
    order_item_list = []

    order_data = {
        "buyer_id": req_user["_id"],
        "items": [],
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "status": OrderStatus.PENDING,
        "total_price": 0.0,
    }
    order = await db["orders"].insert_one(order_data)

    for item in order_items:
        product = await db["products"].find_one({"_id": PyObjectId(item["product_id"])})
        item_info = {
            "order_id": str(order.inserted_id),
            "product_id": item["product_id"],
            "product_name": product["name"],
            "product_description": product["description"],
            "price": float(product["price_per_unit"]),
            "quantity": item["quantity"],
            "subtotal": float(product["price_per_unit"]) * item["quantity"],
        }
        order_item_list.append(item_info)

    await db["orders"].update_one(
        {"_id": PyObjectId(order.inserted_id)},
        {
            "$push": {"items": {"$each": [item for item in order_item_list]}},
            "$set": {
                "updated_at": datetime.now(),
                "total_price": sum([item["subtotal"] for item in order_item_list]),
            },
        },
    )
    return order_item_list


@router.patch("/{id}")
async def update_order(
    id: str,
    payload: OrderCreateSchema,
    current_user=Depends(auth_handler.auth_wrapper),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    req_user = await get_current_user(current_user, db)
    if not hasRetailerPermission(req_user):
        msg = "Not allowed, contact Administrator"
        raise HTTPException(status_code=403, detail=msg)

    return payload.dict()


@router.delete("/{id}")
async def delete_order(
    id: str,
    current_user=Depends(auth_handler.auth_wrapper),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    req_user = await get_current_user(current_user, db)
    if not (hasAdminPermission(req_user) or hasRetailerPermission(req_user)):
        msg = "Not allowed, contact Administrator"
        raise HTTPException(status_code=403, detail=msg)

    await db["orders"].delete_one({"_id": PyObjectId(id)})
