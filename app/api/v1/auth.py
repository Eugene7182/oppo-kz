from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, TokenPair, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(or_(User.username == payload.username, User.email == payload.username)).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    user.last_login_at = datetime.utcnow()
    db.add(user); db.commit()
    return TokenPair(access_token=create_access_token(user.id), refresh_token=create_refresh_token(user.id))

@router.post("/refresh", response_model=TokenPair)
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    user = db.get(User, payload.get("sub"))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User disabled or not found")
    return TokenPair(access_token=create_access_token(user.id), refresh_token=create_refresh_token(user.id))

@router.get("/me", response_model=UserRead)
def me(current: User = Depends(get_current_user)):
    return current
