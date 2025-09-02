from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from pydantic import ConfigDict


# ======== AUTH ========

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class RefreshInput(BaseModel):
    refresh_token: str


# ======== INVITES ========

class InviteCreateIn(BaseModel):
    """
    Входная модель для создания инвайта.
    """
    email: EmailStr
    role: str = Field(default="promoter", description="Role for invited user")
    note: Optional[str] = None
    # Можно задать либо относительный срок, либо конкретную дату
    expires_in_days: Optional[int] = Field(default=7, ge=1, le=365)
    expires_at: Optional[datetime] = None


class InviteOut(BaseModel):
    id: int
    email: EmailStr
    code: str
    role: str
    note: Optional[str] = None
    expires_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class InviteCreateOut(InviteOut):
    """Ответ после создания инвайта (тот же payload, что и InviteOut)."""
    pass


class InviteCheckOut(BaseModel):
    """
    Ответ для проверки инвайта по коду.
    """
    exists: bool
    valid: bool
    reason: Optional[str] = None  # например: "expired", "already_used", "not_found"
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    expires_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
