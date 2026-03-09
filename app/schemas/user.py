from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_verified: bool
    auth_provider: str
    created_at: datetime
    updated_at: datetime

class UserRegister(UserBase):
    password: str
    confirm_password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyAccountRequest(BaseModel):
    email: EmailStr
    otp: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ResendOTPRequest(BaseModel):
    email: EmailStr
    type: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class MessageResponse(BaseModel):
    message: str

class GoogleAuthRequest(BaseModel):
    id_token: str

class GuestUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    auth_provider: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    created_at: datetime
