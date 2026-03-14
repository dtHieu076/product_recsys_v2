from sqlalchemy import Column, BigInteger, String, Numeric, text
from sqlalchemy.ext.hybrid import hybrid_property
from .user import Base

class Product(Base):
    __tablename__ = "products"

    product_id = Column(BigInteger, primary_key=True)
    category_id = Column(BigInteger)
    brand = Column(String)
    price = Column(Numeric(10,2))
    product_name = Column(String)
    image_url = Column(String)

    @hybrid_property
    def name(self):
        return self.product_name

    @hybrid_property
    def description(self):
        return f"{self.brand} product"

