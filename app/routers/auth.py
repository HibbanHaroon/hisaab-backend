from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from ..utils.db_utils import get_db
from ..utils.auth_utils import get_password_hash, verify_password
from ..utils.email_utils import generate_otp, send_otp_email
from ..utils.jwt_utils import create_access_token, create_refresh_token, verify_token
from ..models import User, VerificationCode
from ..schemas.user import (
    UserRegister, UserResponse, LoginRequest, VerifyAccountRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
    ResendOTPRequest, TokenResponse, MessageResponse
)
from ..exceptions import CustomHTTPException
from ..constants.error_messages import (
    PASSWORD_MISMATCH, EMAIL_EXISTS, INVALID_CREDENTIALS,
    INVALID_OTP, USER_NOT_FOUND, UNVERIFIED_ACCOUNT,
    INVALID_REFRESH_TOKEN, ALREADY_VERIFIED
)
from ..constants.endpoints import (
    REGISTER, LOGIN, VERIFY_ACCOUNT, FORGOT_PASSWORD,
    RESET_PASSWORD, REFRESH, RESEND_OTP
)
from ..constants.otp_types import OTPType
from ..settings import settings

security = HTTPBearer()
router = APIRouter()

def _generate_tokens(user: User) -> dict:
    token_data = {"sub": user.email, "user_id": user.id}
    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer"
    }

def _create_and_send_otp(db: Session, user: User, otp_type: str) -> str:
    db.query(VerificationCode).filter(
        VerificationCode.user_id == user.id,
        VerificationCode.type == otp_type
    ).delete()

    otp = generate_otp()
    expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    verification_code = VerificationCode(
        user_id=user.id,
        code=otp,
        expires_at=expiry,
        type=otp_type
    )
    db.add(verification_code)
    db.commit()
    return otp

@router.post(REGISTER, response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, db: Session = Depends(get_db)) -> UserResponse:
    if user.password != user.confirm_password:
        raise CustomHTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=PASSWORD_MISMATCH)

    if db.query(User).filter(User.email == user.email).first():
        raise CustomHTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=EMAIL_EXISTS)

    try:
        db_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=get_password_hash(user.password),
            is_verified=False,
            auth_provider="password"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        otp = _create_and_send_otp(db, db_user, OTPType.EMAIL_VERIFY)
        await send_otp_email(db_user.email, otp, OTPType.EMAIL_VERIFY)

        return UserResponse.model_validate(db_user)
    except CustomHTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise CustomHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating user"
        ) from e

@router.post(VERIFY_ACCOUNT, response_model=TokenResponse)
async def verify_account(request: VerifyAccountRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise CustomHTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND)

    code_record = db.query(VerificationCode).filter(
        VerificationCode.user_id == user.id,
        VerificationCode.code == request.otp,
        VerificationCode.type == OTPType.EMAIL_VERIFY
    ).first()

    if not code_record or code_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise CustomHTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_OTP)

    user.is_verified = True
    db.delete(code_record)
    db.commit()

    return _generate_tokens(user)

@router.post(LOGIN, response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not user.password:
        raise CustomHTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)

    if not verify_password(request.password, user.password):
        raise CustomHTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)

    if not user.is_verified:
        raise CustomHTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNVERIFIED_ACCOUNT)

    return _generate_tokens(user)

@router.post(FORGOT_PASSWORD, response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)) -> MessageResponse:
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        return MessageResponse(message="If the email exists, an OTP has been sent.")

    otp = _create_and_send_otp(db, user, OTPType.PASSWORD_RESET)
    await send_otp_email(user.email, otp, OTPType.PASSWORD_RESET)

    return MessageResponse(message="If the email exists, an OTP has been sent.")

@router.post(RESET_PASSWORD, response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)) -> MessageResponse:
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise CustomHTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_OTP)

    code_record = db.query(VerificationCode).filter(
        VerificationCode.user_id == user.id,
        VerificationCode.code == request.otp,
        VerificationCode.type == OTPType.PASSWORD_RESET
    ).first()

    if not code_record or code_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise CustomHTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_OTP)

    user.password = get_password_hash(request.new_password)
    db.delete(code_record)
    db.commit()

    return MessageResponse(message="Password successfully reset.")

@router.post(REFRESH, response_model=TokenResponse)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> TokenResponse:
    payload = verify_token(credentials.credentials, expected_type="refresh")
    if not payload:
        raise CustomHTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_REFRESH_TOKEN)

    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user:
        raise CustomHTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=USER_NOT_FOUND)

    return _generate_tokens(user)

@router.post(RESEND_OTP, response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def resend_otp(request: ResendOTPRequest, db: Session = Depends(get_db)) -> MessageResponse:
    if request.type not in (OTPType.EMAIL_VERIFY, OTPType.PASSWORD_RESET):
        raise CustomHTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid OTP type. Must be '{OTPType.EMAIL_VERIFY}' or '{OTPType.PASSWORD_RESET}'.")

    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        return MessageResponse(message="If the email exists, a new OTP has been sent.")

    if request.type == OTPType.EMAIL_VERIFY and user.is_verified:
        raise CustomHTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ALREADY_VERIFIED)

    otp = _create_and_send_otp(db, user, request.type)
    await send_otp_email(user.email, otp, request.type)

    return MessageResponse(message="If the email exists, a new OTP has been sent.")
