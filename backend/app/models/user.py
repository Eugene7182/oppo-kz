from __future__ import annotations

"""User model and roles."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class UserRole(str, enum.Enum):
    """Список ролей пользователя."""

    admin = "admin"
    office = "office"
    supervisor = "supervisor"
    promoter = "promoter"


class User(Base):
    """User database model."""

    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_role", "role"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="userrole", native_enum=True), nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


__all__ = ["User", "UserRole"]
