from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..utils.db_utils import get_db, get_category_by_id
from ..utils.dependencies import get_current_user
from ..models.user import User
from ..models.category import Category
from ..schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from ..schemas.user import MessageResponse
from ..exceptions import CustomHTTPException
from ..constants.error_messages import CATEGORY_NOT_FOUND, CATEGORY_ALREADY_EXISTS

router = APIRouter()

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if category with same name exists for user
    existing = db.query(Category).filter_by(user_id=current_user.id, name=category_in.name).first()
    if existing:
            raise CustomHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=CATEGORY_ALREADY_EXISTS
            )
    
    category = Category(
        user_id=current_user.id,
        name=category_in.name,
        description=category_in.description,
        color=category_in.color
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.get("", response_model=List[CategoryResponse])
async def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    categories = db.query(Category).filter_by(user_id=current_user.id).all()
    return categories

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = get_category_by_id(db, category_id, current_user.id)
    if not category:
        raise CustomHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CATEGORY_NOT_FOUND
        )
    return category

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = get_category_by_id(db, category_id, current_user.id)
    if not category:
        raise CustomHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CATEGORY_NOT_FOUND
        )
        
    if category_update.name is not None and category_update.name != category.name:
        existing = db.query(Category).filter_by(user_id=current_user.id, name=category_update.name).first()
        if existing:
            raise CustomHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )

    update_data = category_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
        
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{category_id}", response_model=MessageResponse)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = get_category_by_id(db, category_id, current_user.id)
    if not category:
        raise CustomHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CATEGORY_NOT_FOUND
        )
        
    db.delete(category)
    db.commit()
    return MessageResponse(message="Category deleted successfully")