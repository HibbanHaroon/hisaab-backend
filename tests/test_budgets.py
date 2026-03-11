import pytest
from fastapi.testclient import TestClient
from app.constants.endpoints import BASE_URL, AUTH, GUEST_AUTH, CATEGORY, BUDGET

CATEGORY_BASE = f"{BASE_URL}{CATEGORY}"
BUDGET_BASE = f"{BASE_URL}{BUDGET}"

@pytest.fixture
def auth_headers(client: TestClient):
    response = client.post(f"{BASE_URL}{AUTH}{GUEST_AUTH}")
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def category(client: TestClient, auth_headers):
    response = client.post(
        CATEGORY_BASE,
        headers=auth_headers,
        json={"name": "Housing"}
    )
    return response.json()

@pytest.fixture
def budget(client: TestClient, auth_headers, category):
    response = client.post(
        BUDGET_BASE,
        headers=auth_headers,
        json={"category_id": category["id"], "total_amount": 1000.0}
    )
    return response.json()

def test_create_budget(client: TestClient, auth_headers, category):
    response = client.post(
        BUDGET_BASE,
        headers=auth_headers,
        json={"category_id": category["id"], "total_amount": 500.0}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["total_amount"] == 500.0
    assert data["amount_spent"] == 0.0
    assert data["amount_left"] == 500.0

def test_create_budget_duplicate(client: TestClient, auth_headers, budget):
    response = client.post(
        BUDGET_BASE,
        headers=auth_headers,
        json={"category_id": budget["category_id"], "total_amount": 1000.0}
    )
    assert response.status_code == 400

def test_get_budgets(client: TestClient, auth_headers, budget):
    response = client.get(BUDGET_BASE, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["total_amount"] == 1000.0
    assert data[0]["amount_spent"] == 0.0
    assert data[0]["amount_left"] == 1000.0

def test_update_budget(client: TestClient, auth_headers, budget):
    response = client.put(
        f"{BUDGET_BASE}/{budget['id']}",
        headers=auth_headers,
        json={"total_amount": 1200.0}
    )
    assert response.status_code == 200
    assert response.json()["total_amount"] == 1200.0
    assert response.json()["amount_left"] == 1200.0

def test_delete_budget(client: TestClient, auth_headers, budget):
    response = client.delete(f"{BUDGET_BASE}/{budget['id']}", headers=auth_headers)
    assert response.status_code == 200
    
    response2 = client.get(f"{BUDGET_BASE}/{budget['id']}", headers=auth_headers)
    assert response2.status_code == 404
