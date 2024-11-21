from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

from app.core._id import PyObjectId


class OrderStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price_per_unit: float


class Order(BaseModel):
    id: Optional[str] = Field(default_factory=PyObjectId, alias="_id")
    buyer_id: str = Field(..., description="The Retailer who placed the order")
    seller_id: str = Field(..., description="The Wholesaler selling the products")
    items: List[OrderItem]
    total_price: float = 0.0
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

