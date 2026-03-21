from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.product import Product
from app.schemas.product_schema import ProductOut, PaginatedProducts
from typing import List

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=PaginatedProducts)
def get_products(page: int = Query(1, ge=1), limit: int = Query(12, ge=1, le=100), db: Session = Depends(get_db)):
    total = db.query(Product).count()
    products = db.query(Product).offset((page - 1) * limit).limit(limit).all()
    return {"products": products, "total": total, "page": page, "limit": limit}

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

