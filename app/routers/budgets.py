from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..utils.db_utils import get_db, get_budget_amount_spent, get_category_by_id, get_budget_by_id
from ..utils.dependencies import get_current_user
from ..models.user import User
from ..models.category import Category
from ..models.budget import Budget
from ..models.expense import Expense
from ..schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse
from ..schemas.user import MessageResponse
from ..exceptions import CustomHTTPException
from ..constants.error_messages import BUDGET_NOT_FOUND, BUDGET_ALREADY_EXISTS, CATEGORY_NOT_FOUND_OR_UNAUTHORIZED

router = APIRouter()

@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_in: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify category exists and belongs to user
    category = get_category_by_id(db, budget_in.category_id, current_user.id)
    if not category:
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=CATEGORY_NOT_FOUND_OR_UNAUTHORIZED
        )

    # Check if budget already exists for this category
    existing = db.query(Budget).filter_by(category_id=budget_in.category_id, user_id=current_user.id).first()
    if existing:
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=BUDGET_ALREADY_EXISTS
        )

    budget = Budget(
        user_id=current_user.id,
        category_id=budget_in.category_id,
        total_amount=budget_in.total_amount
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    
    # Calculate amount spent for this new budget (should be 0 or based on existing expenses in category)
    amount_spent = get_budget_amount_spent(db, budget.category_id, current_user.id)
    amount_left = budget.total_amount - amount_spent
    return {**budget.__dict__, "amount_spent": amount_spent, "amount_left": amount_left}

@router.get("", response_model=List[BudgetResponse])
async def get_budgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budgets = db.query(Budget).filter_by(user_id=current_user.id).all()
    
    result = []
    for budget in budgets:
        amount_spent = get_budget_amount_spent(db, budget.category_id, current_user.id)
        amount_left = budget.total_amount - amount_spent
        result.append({**budget.__dict__, "amount_spent": amount_spent, "amount_left": amount_left})
        
    return result

@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budget = get_budget_by_id(db, budget_id, current_user.id)
    if not budget:
        raise CustomHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=BUDGET_NOT_FOUND
        )
        
    amount_spent = get_budget_amount_spent(db, budget.category_id, current_user.id)
    amount_left = budget.total_amount - amount_spent
    return {**budget.__dict__, "amount_spent": amount_spent, "amount_left": amount_left}

@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int,
    budget_update: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budget = get_budget_by_id(db, budget_id, current_user.id)
    if not budget:
        raise CustomHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=BUDGET_NOT_FOUND
        )
        
    update_data = budget_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(budget, key, value)
        
    db.commit()
    db.refresh(budget)
    
    amount_spent = get_budget_amount_spent(db, budget.category_id, current_user.id)
    amount_left = budget.total_amount - amount_spent
    return {**budget.__dict__, "amount_spent": amount_spent, "amount_left": amount_left}

@router.delete("/{budget_id}", response_model=MessageResponse)
async def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budget = get_budget_by_id(db, budget_id, current_user.id)
    if not budget:
        raise CustomHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=BUDGET_NOT_FOUND
        )
        
    db.delete(budget)
    db.commit()
    return MessageResponse(message="Budget deleted successfully")