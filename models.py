from sqlalchemy import Column, String
from database import Base


class User(Base):
    __tablename__ = 'users'

    username = Column(String(50), primary_key=True, unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)


