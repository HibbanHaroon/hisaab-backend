from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .db_utils import get_db
from .jwt_utils import verify_token
from ..models.user import User
from ..exceptions import CustomHTTPException
from ..constants.error_messages import INVALID_ACCESS_TOKEN, USER_NOT_FOUND

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    payload = verify_token(credentials.credentials, expected_type="access")
    if not payload:
        raise CustomHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_ACCESS_TOKEN
        )

    print(payload)
    
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user:
        raise CustomHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=USER_NOT_FOUND
        )
    return user
