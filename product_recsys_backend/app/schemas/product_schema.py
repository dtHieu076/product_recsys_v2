from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from decimal import Decimal

class ProductOut(BaseModel):
    product_id: int
    name: str = Field(..., alias='product_name')  # Map from hybrid/DB
    brand: str
    price: float  # DB Numeric -> float
    image_url: str
    category_id: int
    description: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

from typing import List

class PaginatedProducts(BaseModel):
    products: List[ProductOut]
    total: int
    page: int
    limit: int

    model_config = ConfigDict(from_attributes=True)

