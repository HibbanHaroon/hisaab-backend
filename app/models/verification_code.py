from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base

class VerificationCode(Base):
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    type = Column(String(50), nullable=False)
    
    user = relationship("User", back_populates="verification_codes")
