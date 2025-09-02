# backend/app/schemas/user.py
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class UserOut(BaseModel):
    """
    Выходная схема пользователя для /auth/me и других ручек.
    Поля согласованы с твоей ORM-моделью User (из app.models).
    """
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: str  # Enum на стороне БД, сюда прилетит строка
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
