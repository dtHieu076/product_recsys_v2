from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship
from .user import Base

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(BigInteger, primary_key=True)
    category_code = Column(String)

    products = relationship("Product", back_populates="category")

