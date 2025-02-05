from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from ..db import Base

class Category(Base):
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    color = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())