import os
import random
import string
import logging
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from ..settings import settings
from ..constants.otp_types import OTPType

logger = logging.getLogger(__name__)

TEMPLATE_FOLDER = Path(__file__).resolve().parent.parent / "templates"

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=TEMPLATE_FOLDER
)

def generate_otp(length: int = 6) -> str:
    return ''.join(random.choice(string.digits) for _ in range(length))

async def send_otp_email(to_email: str, otp: str, type: str) -> None:
    template_map = {
        OTPType.EMAIL_VERIFY: "verify_account.html",
        OTPType.PASSWORD_RESET: "reset_password.html",
    }

    subject_map = {
        OTPType.EMAIL_VERIFY: "Hisaab - Verify Your Account",
        OTPType.PASSWORD_RESET: "Hisaab - Reset Your Password",
    }

    template_name = template_map.get(type, "verify_account.html")
    subject = subject_map.get(type, "Hisaab OTP")

    message = MessageSchema(
        subject=subject,
        recipients=[to_email],
        template_body={"otp": otp, "expiry_minutes": settings.OTP_EXPIRE_MINUTES},
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message, template_name=template_name)
        logger.info(f"OTP email sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
