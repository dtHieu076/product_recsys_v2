from sqlalchemy.orm import Session
from app.models.event import Event
from app.schemas.event_schema import EventCreate
from app.models.event import EventType
from datetime import datetime

def create_event(db: Session, event: EventCreate):
    # Lớp phòng thủ thép: Lấy giá trị và ép thẳng về chữ thường!
    actual_event_type = (
        event.event_type.value if hasattr(event.event_type, 'value') 
        else str(event.event_type).lower()
    )

    db_event = Event(
        event_time=event.event_time,
        event_type=actual_event_type, # Dùng biến đã được "bảo kê" ở đây
        product_id=event.product_id,
        user_id=event.user_id,
        user_session=event.user_session
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

