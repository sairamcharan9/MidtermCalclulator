"""
Unit Tests for Pydantic Schemas
================================

Tests UserCreate and UserRead schema validation and serialization.
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
from app.schemas import UserCreate, UserRead


class TestUserCreateSchema:
    """Tests for the UserCreate Pydantic schema."""

    def test_valid_user_create(self):
        """UserCreate accepts valid username, email, and password."""
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="securepassword123",
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "securepassword123"

    def test_invalid_email_rejected(self):
        """UserCreate rejects an invalid email format."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="not-an-email",
                password="password123",
            )
        assert "email" in str(exc_info.value).lower()

    def test_missing_username_rejected(self):
        """UserCreate requires a username field."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                password="password123",
            )

    def test_missing_email_rejected(self):
        """UserCreate requires an email field."""
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                password="password123",
            )

    def test_missing_password_rejected(self):
        """UserCreate requires a password field."""
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="test@example.com",
            )

    def test_email_with_subdomain(self):
        """UserCreate accepts emails with subdomains."""
        user = UserCreate(
            username="testuser",
            email="user@mail.example.com",
            password="password123",
        )
        assert user.email == "user@mail.example.com"


class TestUserReadSchema:
    """Tests for the UserRead Pydantic schema."""

    def test_valid_user_read(self):
        """UserRead correctly serializes user data."""
        now = datetime.now(timezone.utc)
        user = UserRead(
            id=1,
            username="testuser",
            email="test@example.com",
            created_at=now,
        )
        assert user.id == 1
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.created_at == now

    def test_user_read_excludes_password_hash(self):
        """UserRead schema does NOT include a password_hash field."""
        now = datetime.now(timezone.utc)
        user = UserRead(
            id=1,
            username="testuser",
            email="test@example.com",
            created_at=now,
        )
        user_dict = user.model_dump()
        assert "password_hash" not in user_dict
        assert "password" not in user_dict

    def test_user_read_from_orm_object(self):
        """UserRead can be created from an ORM-like object (from_attributes)."""

        class FakeUser:
            id = 1
            username = "ormuser"
            email = "orm@example.com"
            password_hash = "$2b$12$somehash"
            created_at = datetime.now(timezone.utc)

        user = UserRead.model_validate(FakeUser())
        assert user.username == "ormuser"
        assert user.email == "orm@example.com"
        # password_hash should NOT appear in the serialized output
        assert "password_hash" not in user.model_dump()

    def test_user_read_missing_id_rejected(self):
        """UserRead requires an id field."""
        with pytest.raises(ValidationError):
            UserRead(
                username="testuser",
                email="test@example.com",
                created_at=datetime.now(timezone.utc),
            )
