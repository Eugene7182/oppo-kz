# app/models/user.py
from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from uuid import uuid4

from sqlalchemy import Enum as SAEnum, String, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base

class UserRole(str, PyEnum):
    admin = "admin"
    office = "office"
    supervisor = "supervisor"   # добавили роль
    promoter = "promoter"

class User(Base):
    __tablename__ = "users"

    # Храним UUID как строку — кросс-БД и читаемо
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))

    # Логин по username (обязательно) и/или email (опционально)
    username: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), unique=True, index=True, nullable=True)

    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Важно: фиксированное имя типа 'userrole' и native_enum=True для Postgres
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="userrole", native_enum=True),
        nullable=False,
        index=True,
        default=UserRole.promoter,
    )

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_users_username", "username"),
        Index("ix_users_email", "email"),
        Index("ix_users_role", "role"),
    )
