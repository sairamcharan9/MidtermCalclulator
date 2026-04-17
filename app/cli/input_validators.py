"""
Input Validation (Look Before You Leap)
=======================================

Provides functions for validating user input before any calculations are attempted.
"""

from decimal import Decimal, InvalidOperation
from app.cli.calculation import CalculationFactory


def validate_input_parts(parts: list[str], max_value: float = 1e10) -> str | None:
    """
    Validates that the tokenized user input is in the correct format for a calculation.

    Returns an error message string if validation fails, or None if it succeeds.
    """
    if not parts:
        return "Error: No input provided. Please enter a command."

    operation = parts[0]
    valid_operations = CalculationFactory.get_supported_operations()

    if operation not in valid_operations:
        return (
            f"Error: Unknown operation '{operation}'.\n"
            f"Available operations: {', '.join(valid_operations)}\n"
            "Type 'help' for more information."
        )

    if len(parts) != 3:
        return (
            "Error: Invalid format. Please use: <operation> <number1> <number2>\n"
            "Example: add 5 3\n"
            "Type 'help' for available commands."
        )

    for i in [1, 2]:
        operand_str = parts[i]
        numeric_value = validate_numeric(operand_str)

        if numeric_value is None:
            return f"Error: '{parts[i]}' is not a valid number."

        if abs(numeric_value) > Decimal(str(max_value)):
            return f"Error: Operand '{parts[i]}' exceeds the maximum allowed value of {max_value}."

    return None


def validate_numeric(value: str) -> Decimal | None:
    """Checks if a string can be converted to a `Decimal`."""
    try:
        return Decimal(value)
    except InvalidOperation:
        return None
