from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..db import SessionLocal
from ..models.expense import Expense
from ..models.category import Category
from ..models.budget import Budget

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

def get_budget_amount_spent(db: Session, category_id: int, user_id: int) -> float:
    return db.query(func.sum(Expense.amount)).filter_by(
        category_id=category_id, 
        user_id=user_id
    ).scalar() or 0.0

def get_category_by_id(db: Session, category_id: int, user_id: int) -> Category | None:
    return db.query(Category).filter_by(id=category_id, user_id=user_id).first()

def get_expense_by_id(db: Session, expense_id: int, user_id: int) -> Expense | None:
    return db.query(Expense).filter_by(id=expense_id, user_id=user_id).first()

def get_budget_by_id(db: Session, budget_id: int, user_id: int) -> Budget | None:
    return db.query(Budget).filter_by(id=budget_id, user_id=user_id).first()