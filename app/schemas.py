"""
Pydantic Schemas
================

Defines request/response schemas for User and Calculation operations.

Design notes:
- CalculationCreate: pure schema for validation logic (no user_id).
- CalculationRequest: HTTP body for POST /calculations (adds user_id).
- CalculationUpdate: HTTP body for PUT /calculations/{id} (a, b, type only).
- UserLogin: HTTP body for POST /users/login.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, model_validator


# ---------------------------------------------------------------------------
# User Schemas
# ---------------------------------------------------------------------------

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


class UserLogin(BaseModel):
    """
    Schema for user login requests.

    Fields:
        username: The account username.
        password: The plain-text password to verify.
    """
    username: str
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


# ---------------------------------------------------------------------------
# Calculation Schemas
# ---------------------------------------------------------------------------

class OperationType(str, Enum):
    ADD = "ADD"
    SUBTRACT = "SUBTRACT"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    INT_DIVIDE = "INT_DIVIDE"


class CalculationCreate(BaseModel):
    """
    Core schema for validating incoming calculation data.

    This schema is used for unit tests and as the base for HTTP request bodies.
    It validates operand types, operation type enum, and blocks division by zero.

    Fields:
        a: First operand.
        b: Second operand.
        type: Arithmetic operation (ADD, SUBTRACT, MULTIPLY, DIVIDE, INT_DIVIDE).
    """
    a: float
    b: float
    type: OperationType

    @model_validator(mode='after')
    def check_division_by_zero(self):
        if self.type in (OperationType.DIVIDE, OperationType.INT_DIVIDE) and self.b == 0:
            raise ValueError("Cannot divide by zero")
        return self


class CalculationRequest(CalculationCreate):
    """
    HTTP request body for POST /calculations.

    Extends CalculationCreate with user_id, which identifies the owner.
    Division-by-zero validation is inherited from CalculationCreate.

    Fields:
        user_id: ID of the user creating this calculation.
    """
    user_id: int


class CalculationUpdate(BaseModel):
    """
    HTTP request body for PUT /calculations/{id}.

    All fields are required; the result is recomputed server-side.
    user_id is NOT updatable via PUT (preserved from the original record).

    Fields:
        a: Updated first operand.
        b: Updated second operand.
        type: Updated arithmetic operation.
    """
    a: float
    b: float
    type: OperationType

    @model_validator(mode='after')
    def check_division_by_zero(self):
        if self.type in (OperationType.DIVIDE, OperationType.INT_DIVIDE) and self.b == 0:
            raise ValueError("Cannot divide by zero")
        return self


class CalculationRead(BaseModel):
    """
    Schema for returning calculation records in API responses.
    """
    id: int
    a: float
    b: float
    type: str
    result: float
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
