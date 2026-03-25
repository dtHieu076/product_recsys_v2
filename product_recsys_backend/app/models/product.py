from sqlalchemy import Column, BigInteger, String, Numeric, text, ForeignKey # Thêm ForeignKey ở đây
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from .user import Base

class Product(Base):
    __tablename__ = "products"

    product_id = Column(BigInteger, primary_key=True)
    
    # SỬA DÒNG NÀY: Thêm ForeignKey trỏ đến bảng categories
    category_id = Column(BigInteger, ForeignKey("categories.category_id")) 
    
    brand = Column(String)
    price = Column(Numeric(10,2))
    product_name = Column(String)
    image_url = Column(String)

    # Relationship giờ đây sẽ hoạt động vì đã có ForeignKey ở trên
    category = relationship("Category", back_populates="products")

    @hybrid_property
    def name(self):
        return self.product_name

    @hybrid_property
    def description(self):
        return f"{self.brand} product"

    @hybrid_property
    def category_code(self):
        # Thuộc tính này sẽ hoạt động sau khi relationship được thiết lập đúng
        return self.category.category_code if self.category else None