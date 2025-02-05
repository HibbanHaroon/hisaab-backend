from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..utils.db_utils import get_db
from ..utils.auth_utils import get_password_hash
from ..models import User
from ..schemas.user import UserRegister, UserResponse
from ..exceptions import CustomHTTPException
from ..constants.error_messages import PASSWORD_MISMATCH, EMAIL_EXISTS
from ..constants.endpoints import REGISTER, LOGIN

router = APIRouter()

@router.post(REGISTER, response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, db: Session = Depends(get_db)) -> UserResponse:
    # Validate passwords match
    if user.password != user.confirm_password:
        raise CustomHTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=PASSWORD_MISMATCH)
    
    # Check if the email already exists
    if db.query(User).filter(User.email == user.email).first():
        raise CustomHTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=EMAIL_EXISTS)
    
    try:
        db_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=get_password_hash(user.password),
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserResponse.model_validate(db_user)
    except Exception as e:
        db.rollback()
        raise CustomHTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating user") from e