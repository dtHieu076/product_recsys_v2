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
    category_code: Optional[str] = Field(default=None, alias='category_code')
    confidence_score: float = Field(default=0.0, description="Độ tin cậy của khuyến nghị (0.0-1.0)")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

from typing import List

class PaginatedProducts(BaseModel):
    products: List[ProductOut]
    total: int
    page: int
    limit: int

    model_config = ConfigDict(from_attributes=True)

