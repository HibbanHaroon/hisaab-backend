from enum import Enum

class OTPType(str, Enum):
    EMAIL_VERIFY = "email_verify"
    PASSWORD_RESET = "password_reset"

class AuthProvider(str, Enum):
    PASSWORD = "password"
    GOOGLE = "google"
    GUEST = "guest"
