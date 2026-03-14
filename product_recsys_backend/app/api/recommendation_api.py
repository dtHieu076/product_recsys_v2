from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.product_schema import ProductOut
from app.services.recommendation_service import RecommendationService
from typing import List

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/{user_id}", response_model=List[ProductOut])
def get_recommendations(user_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    recs = RecommendationService.get_recommendations(db, user_id)
    return recs

