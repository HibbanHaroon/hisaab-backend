import pytest
from fastapi.testclient import TestClient
from app.constants.endpoints import BASE_URL, AUTH, GUEST_AUTH, CATEGORY, EXPENSE, BUDGET

CATEGORY_BASE = f"{BASE_URL}{CATEGORY}"
EXPENSE_BASE = f"{BASE_URL}{EXPENSE}"
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
        json={"name": "Utilities"}
    )
    return response.json()

@pytest.fixture
def expense(client: TestClient, auth_headers, category):
    response = client.post(
        EXPENSE_BASE,
        headers=auth_headers,
        json={"category_id": category["id"], "name": "Electricity Bill", "amount": 150.0}
    )
    return response.json()

def test_create_expense(client: TestClient, auth_headers, category):
    response = client.post(
        EXPENSE_BASE,
        headers=auth_headers,
        json={"category_id": category["id"], "name": "Water Bill", "amount": 50.0}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Water Bill"
    assert data["amount"] == 50.0

def test_get_expenses(client: TestClient, auth_headers, expense):
    response = client.get(EXPENSE_BASE, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["amount"] == 150.0

def test_update_expense(client: TestClient, auth_headers, expense):
    response = client.put(
        f"{EXPENSE_BASE}/{expense['id']}",
        headers=auth_headers,
        json={"amount": 160.0}
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 160.0

def test_delete_expense(client: TestClient, auth_headers, expense):
    response = client.delete(f"{EXPENSE_BASE}/{expense['id']}", headers=auth_headers)
    assert response.status_code == 200
    
    response2 = client.get(f"{EXPENSE_BASE}/{expense['id']}", headers=auth_headers)
    assert response2.status_code == 404

def test_budget_amount_spent_updates(client: TestClient, auth_headers, category):
    budget_res = client.post(
        BUDGET_BASE,
        headers=auth_headers,
        json={"category_id": category["id"], "total_amount": 500.0}
    )
    budget = budget_res.json()
    assert budget["amount_spent"] == 0.0

    client.post(
        EXPENSE_BASE,
        headers=auth_headers,
        json={"category_id": category["id"], "name": "Test", "amount": 100.0}
    )

    budget_get = client.get(f"{BUDGET_BASE}/{budget['id']}", headers=auth_headers)
    assert budget_get.json()["amount_spent"] == 100.0
