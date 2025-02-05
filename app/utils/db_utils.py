from typing import Generator
from sqlalchemy.orm import Session
from ..db import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    Creates a new database session for each request.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()