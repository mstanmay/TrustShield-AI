"""
Auth API — JWT registration, login, token refresh.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.database import User
from app.models.schemas import TokenResponse, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Register a new user."""
    # Check if username/email already exists
    existing = await db.execute(
        select(User).where((User.username == payload.username) | (User.email == payload.email))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username or email already registered")

    user = User(
        id=uuid.uuid4(),
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        created_at=datetime.utcnow(),
    )
    db.add(user)
    await db.flush()

    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        created_at=user.created_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db_session),
):
    """Authenticate and return JWT tokens."""
    result = await db.execute(select(User).where(User.username == payload.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    access_token = create_access_token(data={"sub": str(user.id), "username": user.username})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Refresh an access token using a valid refresh token."""
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("sub")
        result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        new_access = create_access_token(data={"sub": str(user.id), "username": user.username})
        new_refresh = create_refresh_token(data={"sub": str(user.id)})

        return TokenResponse(access_token=new_access, refresh_token=new_refresh)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
