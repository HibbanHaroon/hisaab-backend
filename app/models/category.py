from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base

class Category(Base):
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(500))
    color = Column(String(7))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    expenses = relationship("Expense", back_populates="category")
    budgets = relationship("Budget", back_populates="category")