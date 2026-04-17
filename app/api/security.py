"""
Password Security
=================

Provides password hashing and verification using bcrypt via passlib.
"""

from passlib.context import CryptContext

# Configure bcrypt as the hashing scheme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(raw_password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return pwd_context.hash(raw_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)
