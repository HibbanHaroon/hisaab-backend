import pytest
from fastapi.testclient import TestClient
from app.constants.endpoints import BASE_URL, AUTH, GUEST_AUTH, CATEGORY

CATEGORY_BASE = f"{BASE_URL}{CATEGORY}"

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
        json={"name": "Food", "description": "Groceries and dining out", "color": "#ff0000"}
    )
    return response.json()

def test_create_category(client: TestClient, auth_headers):
    response = client.post(
        CATEGORY_BASE,
        headers=auth_headers,
        json={"name": "Travel", "description": "Flights and hotels", "color": "#00ff00"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Travel"
    assert data["description"] == "Flights and hotels"
    assert "id" in data

def test_create_category_duplicate_name(client: TestClient, auth_headers, category):
    response = client.post(
        CATEGORY_BASE,
        headers=auth_headers,
        json={"name": "Food"}
    )
    assert response.status_code == 400

def test_get_categories(client: TestClient, auth_headers, category):
    response = client.get(CATEGORY_BASE, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(c["name"] == "Food" for c in data)

def test_get_category(client: TestClient, auth_headers, category):
    response = client.get(f"{CATEGORY_BASE}/{category['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Food"

def test_update_category(client: TestClient, auth_headers, category):
    response = client.put(
        f"{CATEGORY_BASE}/{category['id']}",
        headers=auth_headers,
        json={"name": "Updated Food", "color": "#0000ff"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Food"
    assert data["color"] == "#0000ff"
    assert data["description"] == category["description"] 

def test_delete_category(client: TestClient, auth_headers, category):
    response = client.delete(f"{CATEGORY_BASE}/{category['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Category deleted successfully"

    response2 = client.get(f"{CATEGORY_BASE}/{category['id']}", headers=auth_headers)
    assert response2.status_code == 404
