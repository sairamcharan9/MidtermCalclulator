"""
SQLAlchemy User Model
====================

Defines the User table with secure password storage and unique constraints.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


class User(Base):
    """
    User model for the application.

    Attributes:
        id: Primary key, auto-incremented.
        username: Unique username, required.
        email: Unique email address, required.
        password_hash: Bcrypt-hashed password, required.
        created_at: Timestamp when the user was created.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
