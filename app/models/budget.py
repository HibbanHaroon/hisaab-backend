from sqlalchemy import Column, Integer, String, Double, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base

class Budget(Base):
    user_id = Column(Integer, ForeignKey("user.id"))
    category_id = Column(Integer, ForeignKey("category.id"))
    total_amount = Column(Double, nullable=False)

    # Because the name of the cateogry would also be the name of the budget, as it is a budget for that cateogry
    category = relationship("Category", back_populates="budgets")