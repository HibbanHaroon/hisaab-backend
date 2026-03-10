import pytest
from fastapi.testclient import TestClient
from app.constants.endpoints import BASE_URL, AUTH, REGISTER, VERIFY_ACCOUNT, USER, PROFILE
from app.models.user import User

AUTH_BASE = f"{BASE_URL}{AUTH}"
USER_BASE = f"{BASE_URL}{USER}"

@pytest.fixture
def auth_headers(client: TestClient, db_session):
    # Clear existing to avoid conflict if tests leak
    from app.models.user import User
    existing = db_session.query(User).filter(User.email == "testuser@example.com").first()
    if existing:
        db_session.delete(existing)
        db_session.commit()

    client.post(
        f"{AUTH_BASE}{REGISTER}",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
    )
    from app.models.verification_code import VerificationCode
    user = db_session.query(User).filter(User.email == "testuser@example.com").first()
    code_record = db_session.query(VerificationCode).filter(VerificationCode.user_id == user.id).first()
    
    verify_response = client.post(
        f"{AUTH_BASE}{VERIFY_ACCOUNT}",
        json={
            "email": "testuser@example.com",
            "otp": code_record.code
        }
    )
    token = verify_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_user_profile(client: TestClient, auth_headers):
    response = client.get(f"{USER_BASE}{PROFILE}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["first_name"] == "Test"
    assert "country" in data

def test_update_user_profile_patch(client: TestClient, auth_headers):
    response = client.patch(
        f"{USER_BASE}{PROFILE}",
        headers=auth_headers,
        json={"first_name": "Updated", "country": "USA"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["country"] == "USA"
    assert data["last_name"] == "User"

def test_delete_user_account(client: TestClient, auth_headers, db_session):
    response = client.delete(f"{USER_BASE}{PROFILE}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "User account deleted successfully"
    
    db_session.expire_all()
    user = db_session.query(User).filter(User.email == "testuser@example.com").first()
    assert user is None

def test_unauthorized_access(client: TestClient):
    response = client.get(f"{USER_BASE}{PROFILE}")
    assert response.status_code == 401

    response = client.get(f"{USER_BASE}{PROFILE}", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
