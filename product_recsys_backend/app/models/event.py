from sqlalchemy import Column, BigInteger, String, DateTime, Enum as SQLEnum
from enum import Enum
from .user import Base

class EventType(str, Enum):
    VIEW = "view"
    CART = "cart"
    REMOVE_FROM_CART = "remove_from_cart"
    PURCHASE = "purchase"

class Event(Base):
    __tablename__ = "events"

    event_id = Column(BigInteger, primary_key=True)
    event_time = Column(DateTime)
    event_type = Column(SQLEnum(EventType))
    product_id = Column(BigInteger)
    user_id = Column(BigInteger)
    user_session = Column(String)

