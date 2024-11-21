from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ProductStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RESTOCK = "restock"


class ProductCategory(str, Enum):
    GRAINS = "grains"
    VEGETABLES = "vegetables"
    NUTS = "nuts"
    DAIRY = "dairy"
    ROOTS = "roots"
    OTHER = "other"


class ProductCreateSchema(BaseModel):
    name: str
    description: str
    category: str
    unit: str
    price_per_unit: float
    stock_quantity: str
    seller_id: str
    is_available: bool = True
    created_at: datetime = datetime.now()


class ProductDetailSchema(BaseModel):
    id: str
    name: str
    description: str
    category: str
    price_per_unit: float
    stock_quantity: str
    unit: str
    seller_id: str
    is_available: bool
    created_at: datetime = datetime.now()

    class Config:
        from_attributes = True
