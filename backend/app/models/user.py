from __future__ import annotations

"""User model and roles."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class UserRole(str, enum.Enum):
    """Список ролей пользователя."""

    admin = "admin"
    office = "office"
    supervisor = "supervisor"
    promoter = "promoter"


class UserStatus(str, enum.Enum):
    """Статус пользователя."""

    active = "active"
    inactive = "inactive"
    invited = "invited"


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
    hashed_password: Mapped[str] = mapped_column("password_hash", String(255), nullable=False)
    region_id: Mapped[str | None] = mapped_column(
        ForeignKey("regions.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="userstatus", native_enum=True), nullable=False, default=UserStatus.active
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    region = relationship("Region", lazy="joined")

    @hybrid_property
    def is_active(self) -> bool:
        """Совместимость со старым кодом: активен ли пользователь."""

        return self.status == UserStatus.active

    @property
    def password_hash(self) -> str:
        """Alias для совместимости со старой схемой."""

        return self.hashed_password

    @password_hash.setter
    def password_hash(self, value: str) -> None:
        self.hashed_password = value


__all__ = ["User", "UserRole", "UserStatus"]
