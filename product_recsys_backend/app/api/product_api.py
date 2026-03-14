from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.product import Product
from app.schemas.product_schema import ProductOut
from typing import List

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[ProductOut])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

