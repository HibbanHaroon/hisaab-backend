from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import extract

from ..utils.db_utils import get_db, get_category_by_id, get_expense_by_id
from ..utils.dependencies import get_current_user
from ..models.user import User
from ..models.category import Category
from ..models.expense import Expense
from ..schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from ..schemas.user import MessageResponse
from ..exceptions import CustomHTTPException
from ..constants.error_messages import CATEGORY_NOT_FOUND_OR_UNAUTHORIZED, EXPENSE_NOT_FOUND

router = APIRouter()

@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_in: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify category exists and belongs to user
    category = get_category_by_id(db, expense_in.category_id, current_user.id)
    if not category:
            raise CustomHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=CATEGORY_NOT_FOUND_OR_UNAUTHORIZED
            )

    # NOTE: `expense_date` might be None from schema, SQLAlchemy model default=func.now() will handle it.
    expense_data = expense_in.model_dump()
    if expense_data.get("expense_date") is None:
        del expense_data["expense_date"]

    expense = Expense(**expense_data, user_id=current_user.id)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

@router.get("", response_model=List[ExpenseResponse])
async def get_expenses(
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    year: Optional[int] = Query(None, description="Filter by year (e.g., 2024)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Expense).filter_by(user_id=current_user.id)
    
    if month is not None:
        query = query.filter(extract('month', Expense.expense_date) == month)
    if year is not None:
        query = query.filter(extract('year', Expense.expense_date) == year)
        
    expenses = query.all()
    return expenses

@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expense = get_expense_by_id(db, expense_id, current_user.id)
    if not expense:
        raise CustomHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EXPENSE_NOT_FOUND
        )
    return expense

@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expense = get_expense_by_id(db, expense_id, current_user.id)
    if not expense:
        raise CustomHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EXPENSE_NOT_FOUND
        )

    if expense_update.category_id is not None and expense_update.category_id != expense.category_id:
        category = get_category_by_id(db, expense_update.category_id, current_user.id)
        if not category:
            raise CustomHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=CATEGORY_NOT_FOUND_OR_UNAUTHORIZED
            )

    update_data = expense_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(expense, key, value)
        
    db.commit()
    db.refresh(expense)
    return expense

@router.delete("/{expense_id}", response_model=MessageResponse)
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expense = get_expense_by_id(db, expense_id, current_user.id)
    if not expense:
        raise CustomHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EXPENSE_NOT_FOUND
        )
        
    db.delete(expense)
    db.commit()
    return MessageResponse(message="Expense deleted successfully")