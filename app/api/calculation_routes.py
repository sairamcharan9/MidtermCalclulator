"""
Calculation API Routes (BREAD)
===============================

Implements Browse, Read, Edit, Add, and Delete endpoints for Calculation records.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.database import get_db
from app.api.models import Calculation, CalculationModelFactory, User
from app.api.schemas import CalculationRequest, CalculationRead, CalculationUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/calculations", tags=["calculations"])


@router.get("/", response_model=List[CalculationRead])
def browse_calculations(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db),
):
    """Return all calculations, optionally filtered by user_id."""
    query = db.query(Calculation)
    if user_id is not None:
        query = query.filter(Calculation.user_id == user_id)
    return query.order_by(Calculation.id).all()


@router.get("/{calculation_id}", response_model=CalculationRead)
def read_calculation(calculation_id: int, db: Session = Depends(get_db)):
    """Retrieve a single calculation by its primary key. Returns 404 if not found."""
    calc = db.query(Calculation).filter(Calculation.id == calculation_id).first()
    if calc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Calculation with id={calculation_id} not found.",
        )
    return calc


@router.post("/", response_model=CalculationRead, status_code=status.HTTP_201_CREATED)
def add_calculation(payload: CalculationRequest, db: Session = Depends(get_db)):
    """
    Create a new calculation record.

    The result is computed server-side. Division by zero is rejected at the schema
    level (422) before reaching the database. Returns 404 if the user doesn't exist.
    """
    user = db.query(User).filter(User.id == payload.user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={payload.user_id} not found.",
        )

    try:
        calc = CalculationModelFactory.create_calculation(
            user_id=payload.user_id,
            a=payload.a,
            b=payload.b,
            operation_type=payload.type.value,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    db.add(calc)
    db.commit()
    db.refresh(calc)

    logger.info("Created calculation id=%d for user_id=%d", calc.id, calc.user_id)
    return calc


@router.put("/{calculation_id}", response_model=CalculationRead)
def edit_calculation(
    calculation_id: int,
    payload: CalculationUpdate,
    db: Session = Depends(get_db),
):
    """
    Replace an existing calculation's operands and operation type.
    The result is recomputed server-side. Returns 404 if not found.
    """
    calc = db.query(Calculation).filter(Calculation.id == calculation_id).first()
    if calc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Calculation with id={calculation_id} not found.",
        )

    try:
        updated = CalculationModelFactory.create_calculation(
            user_id=calc.user_id,
            a=payload.a,
            b=payload.b,
            operation_type=payload.type.value,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    calc.a = updated.a
    calc.b = updated.b
    calc.type = updated.type
    calc.result = updated.result

    db.commit()
    db.refresh(calc)

    logger.info("Updated calculation id=%d", calc.id)
    return calc


@router.delete("/{calculation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(calculation_id: int, db: Session = Depends(get_db)):
    """Permanently delete a calculation record. Returns 204 on success, 404 if not found."""
    calc = db.query(Calculation).filter(Calculation.id == calculation_id).first()
    if calc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Calculation with id={calculation_id} not found.",
        )

    db.delete(calc)
    db.commit()

    logger.info("Deleted calculation id=%d", calculation_id)
