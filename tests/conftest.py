import os

# Set test environment variables before importing app modules
os.environ["PROJECT_NAME"] = "Hisaab"
os.environ["VERSION"] = "1.0.0"
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
os.environ["MAIL_USERNAME"] = "test@example.com"
os.environ["MAIL_PASSWORD"] = "test_password"
os.environ["MAIL_FROM"] = "noreply@test.com"
os.environ["MAIL_SERVER"] = "smtp.example.com"

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import Base
from app.utils.db_utils import get_db

engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(autouse=True)
def mock_send_email():
    with patch("app.utils.email_utils.FastMail.send_message", new_callable=AsyncMock) as mock:
        yield mock

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
