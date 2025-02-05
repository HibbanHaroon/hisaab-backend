from sqlalchemy import Column, Integer, String, Double, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..db import Base

class Expense(Base):
    cateogry_id = Column(Integer, ForeignKey("category.id"))
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    amount = Column(Double, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
