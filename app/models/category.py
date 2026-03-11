from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base

class Category(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    name = Column(String(100), index=True, nullable=False)
    description = Column(String(500))
    color = Column(String(7))

    __table_args__ = (UniqueConstraint('user_id', 'name', name='uix_user_category_name'),)

    expenses = relationship("Expense", back_populates="category")
    budgets = relationship("Budget", back_populates="category")