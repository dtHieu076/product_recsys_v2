from pydantic import BaseModel, ConfigDict, Field
from typing import List

class ProductHistoryOut(BaseModel):
    product_id: int
    product_name: str
    view: int = 0
    cart: int = 0
    purchase: int = 0

    model_config = ConfigDict(from_attributes=True)

class CategoryHistoryOut(BaseModel):
    category: str
    view: int = 0
    cart: int = 0
    purchase: int = 0
    products: List[ProductHistoryOut] = []

    model_config = ConfigDict(from_attributes=True)

