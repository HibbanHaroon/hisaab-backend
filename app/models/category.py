from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from ..db import Base

class Category(Base):
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    color = Column(String)