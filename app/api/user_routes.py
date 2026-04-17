"""
User API Routes
===============

CRUD endpoints for User management with secure password handling.
Includes /register (create) and /login (authenticate + return JWT) endpoints.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.database import get_db
from app.api.models import User
from app.api.schemas import UserCreate, UserLogin, UserRead, Token
from app.api.security import hash_password, verify_password, create_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    - Validates email format and uniqueness via Pydantic + DB constraints.
    - Hashes the password with bcrypt before storing.
    - Returns 409 if username or email is already taken.
    - Returns the created user (without password hash).
    """
    hashed = hash_password(user_data.password)

    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed,
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists.",
        )

    logger.info("Registered user: %s (id=%d)", db_user.username, db_user.id)
    return db_user


# Legacy alias — kept for backward compatibility
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED,
             include_in_schema=False)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Legacy alias for /register."""
    return register_user(user_data, db)


@router.post("/login", response_model=Token)
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT access token.

    - Looks up user by username.
    - Verifies bcrypt password hash.
    - Returns 401 Unauthorized if credentials are invalid.
    - On success, returns a signed JWT (HS256, 30-min expiry by default).
    """
    db_user = db.query(User).filter(User.username == credentials.username).first()

    if db_user is None or not verify_password(credentials.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(db_user.id)})
    logger.info("User logged in: %s (id=%d) — JWT issued", db_user.username, db_user.id)
    return Token(access_token=access_token, token_type="bearer")


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Retrieve a single user by ID."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return db_user


@router.get("/", response_model=List[UserRead])
def list_users(db: Session = Depends(get_db)):
    """Retrieve all users."""
    return db.query(User).all()
