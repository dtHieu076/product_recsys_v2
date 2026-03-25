from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.schemas.event_schema import EventCreate, EventOut
from app.schemas import CategoryHistoryOut
from app.services.event_service import create_event, get_user_history

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventOut, status_code=201)
def log_event(event: EventCreate, db: Session = Depends(get_db)):
    return create_event(db, event)

@router.get("/users/{user_id}/history", response_model=List[CategoryHistoryOut])
def get_user_history_endpoint(user_id: int, db: Session = Depends(get_db)):
    """
    Get user interaction history statistics grouped by category with top 5 products.
    """
    return get_user_history(db, user_id)

