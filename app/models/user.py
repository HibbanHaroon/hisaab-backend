from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base

class User(Base):
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True) # nullable for social/anonymous
    country = Column(String, nullable=True)
    
    is_verified = Column(Boolean, default=False)
    auth_provider = Column(String, default="password") # "password", "google", "anonymous"
    provider_id = Column(String, nullable=True)
    token_version = Column(Integer, default=0, nullable=False)

    expenses = relationship("Expense", backref="user")
    budgets = relationship("Budget", backref="user")
    verification_codes = relationship("VerificationCode", back_populates="user", cascade="all, delete-orphan")