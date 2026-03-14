from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.event_schema import EventCreate, EventOut
from app.services.event_service import create_event

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventOut, status_code=201)
def log_event(event: EventCreate, db: Session = Depends(get_db)):
    return create_event(db, event)

