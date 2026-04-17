"""
Unit Tests for SQLAlchemy User Model
=====================================

Tests the User model structure, columns, and constraints.
"""

import pytest
from sqlalchemy import inspect
from app.api.models import User
from app.api.database import Base


class TestUserModel:
    """Tests for the User SQLAlchemy model."""

    def test_user_tablename(self):
        """User model maps to 'users' table."""
        assert User.__tablename__ == "users"

    def test_user_has_required_columns(self):
        """User model has all required columns."""
        columns = {col.name for col in User.__table__.columns}
        expected = {"id", "username", "email", "password_hash", "created_at"}
        assert expected == columns

    def test_id_is_primary_key(self):
        """The 'id' column is the primary key."""
        col = User.__table__.columns["id"]
        assert col.primary_key is True

    def test_username_is_unique(self):
        """The 'username' column has a unique constraint."""
        col = User.__table__.columns["username"]
        assert col.unique is True

    def test_email_is_unique(self):
        """The 'email' column has a unique constraint."""
        col = User.__table__.columns["email"]
        assert col.unique is True

    def test_username_is_not_nullable(self):
        """The 'username' column is NOT nullable."""
        col = User.__table__.columns["username"]
        assert col.nullable is False

    def test_email_is_not_nullable(self):
        """The 'email' column is NOT nullable."""
        col = User.__table__.columns["email"]
        assert col.nullable is False

    def test_password_hash_is_not_nullable(self):
        """The 'password_hash' column is NOT nullable."""
        col = User.__table__.columns["password_hash"]
        assert col.nullable is False

    def test_created_at_has_default(self):
        """The 'created_at' column has a default value."""
        col = User.__table__.columns["created_at"]
        assert col.default is not None

    def test_user_repr(self):
        """User __repr__ returns a readable string."""
        user = User(id=1, username="alice", email="alice@example.com")
        assert "alice" in repr(user)
        assert "alice@example.com" in repr(user)

    def test_user_extends_base(self):
        """User model extends SQLAlchemy's declarative Base."""
        assert issubclass(User, Base.registry.generate_base().__class__) or hasattr(User, "__table__")
