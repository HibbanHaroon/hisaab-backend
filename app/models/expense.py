from sqlalchemy import Column, Integer, String, Double, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base

class Expense(Base):
    user_id = Column(Integer, ForeignKey("user.id"))
    category_id = Column(Integer, ForeignKey("category.id"))
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    amount = Column(Double, nullable=False)

    category = relationship("Category", back_populates="expenses")
