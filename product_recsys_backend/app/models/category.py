from sqlalchemy import Column, BigInteger, String
from .user import Base

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(BigInteger, primary_key=True)
    category_code = Column(String)

