"""
Integration Tests for User API
===============================

Tests the user CRUD endpoints against a real database (SQLite in-memory for
local testing, PostgreSQL in CI via GitHub Actions service container).
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models import User
from main import app


# ---------- Test Database Setup ----------

SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"  # In-memory SQLite

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Provide a test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test, drop them after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


client = TestClient(app)


# ---------- Test Cases ----------


class TestCreateUser:
    """Tests for POST /users/"""

    def test_create_user_success(self):
        """Creating a user with valid data returns 201 and the user data."""
        response = client.post("/users/", json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "securepassword123",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert "id" in data
        assert "created_at" in data
        # password_hash must NOT be in the response
        assert "password_hash" not in data
        assert "password" not in data

    def test_create_user_password_is_hashed(self):
        """The stored password should be a bcrypt hash, not plain text."""
        client.post("/users/", json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "plaintext_password",
        })
        # Query the database directly to check the stored hash
        db = TestingSessionLocal()
        user = db.query(User).filter(User.username == "bob").first()
        db.close()
        assert user is not None
        assert user.password_hash != "plaintext_password"
        assert user.password_hash.startswith("$2b$")

    def test_duplicate_username_returns_409(self):
        """Creating a user with an existing username returns 409."""
        client.post("/users/", json={
            "username": "alice",
            "email": "alice1@example.com",
            "password": "password123",
        })
        response = client.post("/users/", json={
            "username": "alice",
            "email": "alice2@example.com",
            "password": "password456",
        })
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    def test_duplicate_email_returns_409(self):
        """Creating a user with an existing email returns 409."""
        client.post("/users/", json={
            "username": "user1",
            "email": "shared@example.com",
            "password": "password123",
        })
        response = client.post("/users/", json={
            "username": "user2",
            "email": "shared@example.com",
            "password": "password456",
        })
        assert response.status_code == 409

    def test_invalid_email_returns_422(self):
        """Creating a user with an invalid email returns 422."""
        response = client.post("/users/", json={
            "username": "baduser",
            "email": "not-an-email",
            "password": "password123",
        })
        assert response.status_code == 422

    def test_missing_fields_returns_422(self):
        """Creating a user without required fields returns 422."""
        response = client.post("/users/", json={"username": "incomplete"})
        assert response.status_code == 422


class TestGetUser:
    """Tests for GET /users/{user_id}"""

    def test_get_user_by_id(self):
        """Retrieving an existing user by ID returns the correct data."""
        create_resp = client.post("/users/", json={
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "password123",
        })
        user_id = create_resp.json()["id"]

        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "charlie"
        assert data["email"] == "charlie@example.com"
        assert "password_hash" not in data

    def test_get_nonexistent_user_returns_404(self):
        """Requesting a non-existent user ID returns 404."""
        response = client.get("/users/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestListUsers:
    """Tests for GET /users/"""

    def test_list_users_empty(self):
        """Listing users when none exist returns an empty list."""
        response = client.get("/users/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_users_multiple(self):
        """Listing users returns all created users."""
        client.post("/users/", json={
            "username": "user_a",
            "email": "a@example.com",
            "password": "password",
        })
        client.post("/users/", json={
            "username": "user_b",
            "email": "b@example.com",
            "password": "password",
        })

        response = client.get("/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        usernames = {u["username"] for u in data}
        assert usernames == {"user_a", "user_b"}
