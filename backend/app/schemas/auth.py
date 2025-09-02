from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None


class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class RefreshInput(BaseModel):
    refresh_token: str


class InviteCreateIn(BaseModel):
    email: EmailStr
    role: Optional[str] = None
    store_id: Optional[int] = None
    note: Optional[str] = None


class InviteCreateOut(BaseModel):
    id: int
    email: EmailStr
    code: str
    expires_at: Optional[datetime] = None


class InviteCheckOut(BaseModel):
    email: Optional[EmailStr] = None
    is_valid: bool
    reason: Optional[str] = None


class RegisterByInviteIn(BaseModel):
    code: str
    password: str = Field(min_length=6)
    full_name: Optional[str] = None
    phone: Optional[str] = None
