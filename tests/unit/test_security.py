"""
Unit Tests for Password Security
=================================

Tests hash_password and verify_password functions.
"""

import pytest
from app.security import hash_password, verify_password


class TestHashPassword:
    """Tests for the hash_password function."""

    def test_hash_returns_string(self):
        """hash_password should return a string."""
        result = hash_password("mysecretpassword")
        assert isinstance(result, str)

    def test_hash_is_not_plain_text(self):
        """The hash should NOT be the same as the raw password."""
        raw = "mysecretpassword"
        hashed = hash_password(raw)
        assert hashed != raw

    def test_hash_starts_with_bcrypt_prefix(self):
        """Bcrypt hashes start with '$2b$'."""
        hashed = hash_password("testpassword")
        assert hashed.startswith("$2b$")

    def test_different_calls_produce_different_hashes(self):
        """Each call should produce a different hash due to random salt."""
        raw = "samepassword"
        hash1 = hash_password(raw)
        hash2 = hash_password(raw)
        assert hash1 != hash2

    def test_hash_has_reasonable_length(self):
        """Bcrypt hashes should be 60 characters long."""
        hashed = hash_password("password123")
        assert len(hashed) == 60


class TestVerifyPassword:
    """Tests for the verify_password function."""

    def test_correct_password_returns_true(self):
        """verify_password returns True when the password matches."""
        raw = "correct_password"
        hashed = hash_password(raw)
        assert verify_password(raw, hashed) is True

    def test_wrong_password_returns_false(self):
        """verify_password returns False for an incorrect password."""
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_empty_password_can_be_hashed_and_verified(self):
        """Edge case: empty string password should still work."""
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("notempty", hashed) is False

    def test_long_password(self):
        """Bcrypt handles long passwords (up to 72 bytes)."""
        raw = "a" * 72
        hashed = hash_password(raw)
        assert verify_password(raw, hashed) is True

    def test_special_characters_in_password(self):
        """Passwords with special characters should hash and verify correctly."""
        raw = "p@$$w0rd!#%^&*()"
        hashed = hash_password(raw)
        assert verify_password(raw, hashed) is True
