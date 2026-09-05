import os
os.environ["DATABASE_URL"] = "postgresql://postgres:mypassword123@localhost:5432/finance_tracker_test"

import pytest
from fastapi.testclient import TestClient
from database import Base, engine
import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_signup():
    response = client.post("/signup", json={
        "username": "testuser1",
        "email": "test1@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser1"
    assert "password" not in data


def test_signup_duplicate_username():
    client.post("/signup", json={
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "testpass123"
    })
    response = client.post("/signup", json={
        "username": "testuser2",
        "email": "different@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 400


def test_login_success():
    client.post("/signup", json={
        "username": "testuser3",
        "email": "test3@example.com",
        "password": "testpass123"
    })
    response = client.post("/login", data={
        "username": "testuser3",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password():
    client.post("/signup", json={
        "username": "testuser4",
        "email": "test4@example.com",
        "password": "testpass123"
    })
    response = client.post("/login", data={
        "username": "testuser4",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_create_transaction_requires_auth():
    response = client.post("/transactions", json={
        "amount": 100,
        "note": "test",
        "date": "2026-01-01",
        "category_id": 1
    })
    assert response.status_code == 401


def test_full_transaction_flow():
    client.post("/signup", json={
        "username": "testuser5",
        "email": "test5@example.com",
        "password": "testpass123"
    })
    login_res = client.post("/login", data={
        "username": "testuser5",
        "password": "testpass123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cat_res = client.post("/categories", json={
        "name": "Test Category",
        "type": "expense"
    }, headers=headers)
    assert cat_res.status_code == 200
    category_id = cat_res.json()["id"]

    tx_res = client.post("/transactions", json={
        "amount": 500,
        "note": "test purchase",
        "date": "2026-01-01",
        "category_id": category_id
    }, headers=headers)
    assert tx_res.status_code == 200
    assert tx_res.json()["amount"] == "500.00"

    summary_res = client.get("/summary", headers=headers)
    assert summary_res.status_code == 200
    assert summary_res.json()["total_expense"] == 500