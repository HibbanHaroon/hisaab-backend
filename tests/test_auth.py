from unittest.mock import patch
from fastapi.testclient import TestClient
from app.constants.endpoints import BASE_URL, AUTH, REGISTER, LOGIN, VERIFY_ACCOUNT, FORGOT_PASSWORD, RESET_PASSWORD, REFRESH, RESEND_OTP, GUEST_AUTH, GOOGLE_AUTH
from app.constants.error_messages import UNVERIFIED_ACCOUNT, INVALID_CREDENTIALS, INVALID_OTP, INVALID_REFRESH_TOKEN, ALREADY_VERIFIED, INVALID_GOOGLE_TOKEN, PROVIDER_MISMATCH
from app.constants.otp_types import OTPType

AUTH_BASE = f"{BASE_URL}{AUTH}"

def test_register_user(client: TestClient):
    response = client.post(
        f"{AUTH_BASE}{REGISTER}",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert data["is_verified"] == False

def test_login_unverified(client: TestClient):
    client.post(
        f"{AUTH_BASE}{REGISTER}",
        json={
            "first_name": "Unverified",
            "last_name": "User",
            "email": "unverified@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
    )
    response = client.post(
        f"{AUTH_BASE}{LOGIN}",
        json={
            "email": "unverified@example.com",
            "password": "strongpassword123"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == UNVERIFIED_ACCOUNT

def test_verify_and_login_flow(client: TestClient, db_session):
    client.post(
        f"{AUTH_BASE}{REGISTER}",
        json={
            "first_name": "Verify",
            "last_name": "User",
            "email": "verify@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
    )

    from app.models.verification_code import VerificationCode
    from app.models.user import User

    user = db_session.query(User).filter(User.email == "verify@example.com").first()
    code_record = db_session.query(VerificationCode).filter(VerificationCode.user_id == user.id).first()
    otp = code_record.code

    response = client.post(
        f"{AUTH_BASE}{VERIFY_ACCOUNT}",
        json={
            "email": "verify@example.com",
            "otp": otp
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    login_response = client.post(
        f"{AUTH_BASE}{LOGIN}",
        json={
            "email": "verify@example.com",
            "password": "strongpassword123"
        }
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert "refresh_token" in login_response.json()

def test_refresh_token_flow(client: TestClient, db_session):
    client.post(
        f"{AUTH_BASE}{REGISTER}",
        json={
            "first_name": "Refresh",
            "last_name": "User",
            "email": "refresh@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
    )

    from app.models.verification_code import VerificationCode
    from app.models.user import User

    user = db_session.query(User).filter(User.email == "refresh@example.com").first()
    code_record = db_session.query(VerificationCode).filter(VerificationCode.user_id == user.id).first()

    verify_response = client.post(
        f"{AUTH_BASE}{VERIFY_ACCOUNT}",
        json={"email": "refresh@example.com", "otp": code_record.code}
    )
    refresh_token = verify_response.json()["refresh_token"]

    refresh_response = client.post(
        f"{AUTH_BASE}{REFRESH}",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert refresh_response.status_code == 200
    data = refresh_response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_forgot_and_reset_password(client: TestClient, db_session):
    client.post(
        f"{AUTH_BASE}{REGISTER}",
        json={
            "first_name": "Reset",
            "last_name": "User",
            "email": "reset@example.com",
            "password": "oldpassword123",
            "confirm_password": "oldpassword123"
        }
    )

    from app.models.verification_code import VerificationCode
    from app.models.user import User

    user = db_session.query(User).filter(User.email == "reset@example.com").first()
    verify_code = db_session.query(VerificationCode).filter(VerificationCode.user_id == user.id).first()
    client.post(
        f"{AUTH_BASE}{VERIFY_ACCOUNT}",
        json={"email": "reset@example.com", "otp": verify_code.code}
    )

    forgot_response = client.post(
        f"{AUTH_BASE}{FORGOT_PASSWORD}",
        json={"email": "reset@example.com"}
    )
    assert forgot_response.status_code == 200

    db_session.expire_all()
    reset_code = db_session.query(VerificationCode).filter(
        VerificationCode.user_id == user.id,
        VerificationCode.type == OTPType.PASSWORD_RESET
    ).first()

    reset_response = client.post(
        f"{AUTH_BASE}{RESET_PASSWORD}",
        json={
            "email": "reset@example.com",
            "otp": reset_code.code,
            "new_password": "newpassword456"
        }
    )
    assert reset_response.status_code == 200

    login_response = client.post(
        f"{AUTH_BASE}{LOGIN}",
        json={"email": "reset@example.com", "password": "newpassword456"}
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

def test_invalid_refresh_token(client: TestClient):
    response = client.post(
        f"{AUTH_BASE}{REFRESH}",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == INVALID_REFRESH_TOKEN

def test_refresh_without_token(client: TestClient):
    response = client.post(f"{AUTH_BASE}{REFRESH}")
    assert response.status_code == 401

def test_resend_otp_verify(client: TestClient, db_session):
    client.post(
        f"{AUTH_BASE}{REGISTER}",
        json={
            "first_name": "Resend",
            "last_name": "User",
            "email": "resend@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
    )

    resend_response = client.post(
        f"{AUTH_BASE}{RESEND_OTP}",
        json={"email": "resend@example.com", "type": OTPType.EMAIL_VERIFY}
    )
    assert resend_response.status_code == 200

    from app.models.verification_code import VerificationCode
    from app.models.user import User

    db_session.expire_all()
    user = db_session.query(User).filter(User.email == "resend@example.com").first()
    code_record = db_session.query(VerificationCode).filter(
        VerificationCode.user_id == user.id,
        VerificationCode.type == OTPType.EMAIL_VERIFY
    ).first()

    verify_response = client.post(
        f"{AUTH_BASE}{VERIFY_ACCOUNT}",
        json={"email": "resend@example.com", "otp": code_record.code}
    )
    assert verify_response.status_code == 200
    assert "access_token" in verify_response.json()

def test_resend_otp_already_verified(client: TestClient, db_session):
    client.post(
        f"{AUTH_BASE}{REGISTER}",
        json={
            "first_name": "Already",
            "last_name": "Verified",
            "email": "already@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
    )

    from app.models.verification_code import VerificationCode
    from app.models.user import User

    user = db_session.query(User).filter(User.email == "already@example.com").first()
    code = db_session.query(VerificationCode).filter(VerificationCode.user_id == user.id).first()
    client.post(
        f"{AUTH_BASE}{VERIFY_ACCOUNT}",
        json={"email": "already@example.com", "otp": code.code}
    )

    resend_response = client.post(
        f"{AUTH_BASE}{RESEND_OTP}",
        json={"email": "already@example.com", "type": OTPType.EMAIL_VERIFY}
    )
    assert resend_response.status_code == 400
    assert resend_response.json()["detail"] == ALREADY_VERIFIED

# --- Guest Auth Tests ---

def test_guest_register(client: TestClient):
    response = client.post(f"{AUTH_BASE}{GUEST_AUTH}")
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["auth_provider"] == "guest"
    assert data["email"].startswith("guest_")
    assert data["email"].endswith("@hisaab")

def test_guest_register_creates_unique_users(client: TestClient):
    response1 = client.post(f"{AUTH_BASE}{GUEST_AUTH}")
    response2 = client.post(f"{AUTH_BASE}{GUEST_AUTH}")
    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response1.json()["id"] != response2.json()["id"]
    assert response1.json()["email"] != response2.json()["email"]

def test_guest_login_via_refresh(client: TestClient):
    register_response = client.post(f"{AUTH_BASE}{GUEST_AUTH}")
    assert register_response.status_code == 201
    refresh_token = register_response.json()["refresh_token"]

    refresh_response = client.post(
        f"{AUTH_BASE}{REFRESH}",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()
    assert "refresh_token" in refresh_response.json()

# --- Google Auth Tests ---

MOCK_GOOGLE_PAYLOAD = {
    "sub": "google_user_123",
    "email": "googleuser@gmail.com",
    "given_name": "Google",
    "family_name": "User",
    "email_verified": True,
}

def test_google_auth_new_user(client: TestClient):
    with patch("app.routers.auth.google_id_token.verify_oauth2_token", return_value=MOCK_GOOGLE_PAYLOAD):
        response = client.post(
            f"{AUTH_BASE}{GOOGLE_AUTH}",
            json={"id_token": "valid_google_token"}
        )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_google_auth_existing_user(client: TestClient):
    with patch("app.routers.auth.google_id_token.verify_oauth2_token", return_value=MOCK_GOOGLE_PAYLOAD):
        # First call creates the user
        client.post(f"{AUTH_BASE}{GOOGLE_AUTH}", json={"id_token": "valid_google_token"})
        # Second call logs in the existing user
        response = client.post(f"{AUTH_BASE}{GOOGLE_AUTH}", json={"id_token": "valid_google_token"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_google_auth_provider_mismatch(client: TestClient, db_session):
    # Create a password-based user first
    client.post(
        f"{AUTH_BASE}{REGISTER}",
        json={
            "first_name": "Password",
            "last_name": "User",
            "email": "mismatch@gmail.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
    )

    mismatch_payload = {**MOCK_GOOGLE_PAYLOAD, "email": "mismatch@gmail.com"}
    with patch("app.routers.auth.google_id_token.verify_oauth2_token", return_value=mismatch_payload):
        response = client.post(
            f"{AUTH_BASE}{GOOGLE_AUTH}",
            json={"id_token": "valid_google_token"}
        )
    assert response.status_code == 400
    assert response.json()["detail"] == PROVIDER_MISMATCH

def test_google_auth_invalid_token(client: TestClient):
    with patch("app.routers.auth.google_id_token.verify_oauth2_token", side_effect=ValueError("Invalid token")):
        response = client.post(
            f"{AUTH_BASE}{GOOGLE_AUTH}",
            json={"id_token": "invalid_token"}
        )
    assert response.status_code == 401
    assert response.json()["detail"] == INVALID_GOOGLE_TOKEN
