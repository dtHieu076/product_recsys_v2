from sqlalchemy import Column, BigInteger, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String)
    password = Column(String)

