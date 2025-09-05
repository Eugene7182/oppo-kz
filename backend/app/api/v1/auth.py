"""Authentication and user info endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_current_user,
    rbac_required,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import ErrorResponse, LoginRequest, RefreshRequest, TokenPair, UserRead
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair, responses={401: {"model": ErrorResponse}})
def login(data: LoginRequest, db: Session = Depends(get_db)) -> TokenPair:  # noqa: B008
    """Authenticate user and return JWT pair."""
    user = user_service.get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": "Incorrect email or password", "code": "invalid_credentials"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post(
    "/refresh",
    response_model=TokenPair,
    responses={401: {"model": ErrorResponse}},
)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)) -> TokenPair:  # noqa: B008
    """Refresh JWT tokens using refresh token."""
    user_id = decode_refresh_token(data.refresh_token)
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": "User not found", "code": "invalid_token"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/me", response_model=UserRead, responses={401: {"model": ErrorResponse}})
def me(current_user: User = Depends(get_current_user)) -> User:  # noqa: B008
    """Return current authenticated user."""
    return current_user


# pre-calculate dependency to avoid flake8 B008
_admin_required = rbac_required([UserRole.admin])


@router.get("/ping-admin", dependencies=[Depends(_admin_required)])
def ping_admin() -> dict[str, bool]:
    """RBAC-protected ping."""
    return {"ok": True}


__all__ = ["router"]
