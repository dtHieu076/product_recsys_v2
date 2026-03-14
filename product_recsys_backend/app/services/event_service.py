from sqlalchemy.orm import Session
from app.models.event import Event
from app.schemas.event_schema import EventCreate
from app.models.event import EventType
from datetime import datetime

async def create_event(db: Session, event: EventCreate) -> Event:
    db_event = Event(
        event_type=event.event_type,
        product_id=event.product_id,
        user_id=event.user_id,
        user_session=event.user_session,
        event_time=datetime.utcnow() if event.event_time is None else event.event_time
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

