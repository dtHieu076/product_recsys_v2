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
    
    # SỬA LẠI DÒNG NÀY:
    # 1. values_callable: Ép SQLAlchemy dùng giá trị chữ thường
    # 2. name="action_type": (Tùy chọn nhưng khuyên dùng) Match đúng với tên kiểu ENUM trong PostgreSQL của bạn
    event_type = Column(
        SQLEnum(
            EventType, 
            name="action_type", 
            values_callable=lambda obj: [e.value for e in obj]
        )
    )
    
    product_id = Column(BigInteger)
    user_id = Column(BigInteger)
    user_session = Column(String)