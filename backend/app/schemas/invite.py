"""Pydantic schemas for invite workflow."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, constr

from app.models.invite import InviteScopeType, InviteStatus


class InviteCreate(BaseModel):
    """Запрос на создание приглашения."""

    email: EmailStr
    role_requested: Literal["admin", "office", "supervisor", "promoter"]
    scope_type: InviteScopeType | None = None
    scope_id: constr(max_length=36) | None = None
    ttl_hours: int = Field(default=72, ge=1, le=24 * 14)


class InviteOut(BaseModel):
    """API-ответ с данными приглашения."""

    id: str
    email: EmailStr
    role_requested: str
    scope_type: InviteScopeType | None
    scope_id: str | None
    status: InviteStatus
    expires_at: datetime
    invited_by: str | None


class InviteTokenView(BaseModel):
    """Проверка токена."""

    email: EmailStr
    role_requested: str
    scope_type: InviteScopeType | None
    scope_id: str | None
    status: InviteStatus
    expires_at: datetime
    expired: bool


class InviteAccept(BaseModel):
    """Принятие приглашения."""

    full_name: str
    password: constr(min_length=8)


class InviteList(BaseModel):
    """Пагинация приглашений."""

    items: list[InviteOut]


__all__ = [
    "InviteCreate",
    "InviteOut",
    "InviteTokenView",
    "InviteAccept",
    "InviteList",
]
