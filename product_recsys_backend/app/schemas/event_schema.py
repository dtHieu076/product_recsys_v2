from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.event import EventType
from pydantic import BaseModel, ConfigDict

class EventCreate(BaseModel):
    user_id: int
    product_id: int
    event_type: EventType
    user_session: str
    event_time: Optional[datetime] = None

class EventOut(BaseModel):
    event_id: int
    event_time: datetime
    event_type: EventType
    product_id: int
    user_id: int
    user_session: str

    model_config = ConfigDict(from_attributes=True)

