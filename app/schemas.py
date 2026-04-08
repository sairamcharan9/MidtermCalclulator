"""
Pydantic Schemas
================

Defines request/response schemas for User operations.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    Fields:
        username: The desired username (required).
        email: A valid email address (required).
        password: The plain-text password (required, will be hashed before storage).
    """
    username: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    """
    Schema for returning user data in API responses.
    Intentionally excludes password_hash for security.

    Fields:
        id: The user's database ID.
        username: The user's username.
        email: The user's email address.
        created_at: When the user account was created.
    """
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
