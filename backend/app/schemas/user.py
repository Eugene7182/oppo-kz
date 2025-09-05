from __future__ import annotations

"""Pydantic schemas for user and auth."""

from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserRead(BaseModel):
    """User data returned to clients."""

    id: str
    email: EmailStr
    full_name: str | None = None
    role: UserRole
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {
        "from_attributes": True,
    }


class UserCreateMinimal(BaseModel):
    """Minimal fields to create a user."""

    email: EmailStr
    password: str
    full_name: str | None = None
    role: UserRole = UserRole.promoter


class TokenPair(BaseModel):
    """JWT access/refresh pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Login credentials."""

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
    code: str
