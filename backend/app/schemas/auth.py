# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None
    # секунд до истечения access-токена (если отдаёшь)
    expires_in: Optional[int] = None


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class RefreshInput(BaseModel):
    refresh_token: str


class InviteCreate(BaseModel):
    email: EmailStr
    # в БД это ENUM userrole; здесь оставляем str, чтобы не тянуть БД-_ENUM в код
    role: str = Field(..., max_length=32)
    note: Optional[str] = Field(default=None, max_length=300)
    # можно не передавать — тогда сервер сгенерит срок годности сам
    expires_at: Optional[datetime] = None


class InviteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # для ORM-объектов

    id: int
    email: EmailStr
    role: str
    token: str
    expires_at: Optional[datetime] = None
    used_at: Optional[datetime] = None
    created_by: Optional[int] = None
    note: Optional[str] = None
    created_at: datetime
