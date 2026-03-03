"""
Tests for the Square Root Operation
====================================

This module contains tests for the square root operation, including
edge cases like zero and negative numbers.
"""

import pytest
from decimal import Decimal

from app.exceptions import InvalidOperationError
from app.operations import sqrt


# ---------------------------------------------------------------------------
# sqrt
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "a, expected",
    [
        (Decimal("9"), Decimal("3")),
        (Decimal("0"), Decimal("0")),
        (Decimal("1"), Decimal("1")),
        (Decimal("4"), Decimal("2")),
        (Decimal("0.25"), Decimal("0.5")),
    ],
    ids=["sqrt_9", "sqrt_0", "sqrt_1", "sqrt_4", "sqrt_0.25"],
)
def test_sqrt(a: Decimal, expected: Decimal) -> None:
    """Test sqrt with various positive and zero inputs."""
    assert sqrt(a) == expected


def test_sqrt_negative() -> None:
    """Test that sqrt of a negative number raises InvalidOperationError."""
    with pytest.raises(InvalidOperationError):
        sqrt(Decimal("-9"))
