from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..utils.db_utils import get_db
from ..utils.dependencies import get_current_user
from ..models.user import User
from ..schemas.user import UserResponse, UserUpdate, MessageResponse
from ..exceptions import CustomHTTPException
from ..constants.endpoints import PROFILE

router = APIRouter()

@router.get(PROFILE, response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch(PROFILE, response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    update_data = user_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(current_user, key, value)
        
    try:
        db.commit()
        db.refresh(current_user)
        return current_user
    except Exception as e:
        db.rollback()
        raise CustomHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        ) from e

@router.delete(PROFILE, response_model=MessageResponse)
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        db.delete(current_user)
        db.commit()
        return MessageResponse(message="User account deleted successfully")
    except Exception as e:
        db.rollback()
        raise CustomHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        ) from e
