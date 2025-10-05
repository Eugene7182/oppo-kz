"""Invite model implementing role- and scope-aware onboarding."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class InviteScopeType(str, enum.Enum):
    """Допустимые типы охвата приглашения."""

    country = "country"
    region = "region"
    store = "store"


class InviteStatus(str, enum.Enum):
    """Статус приглашения."""

    pending = "pending"
    accepted = "accepted"
    revoked = "revoked"
    expired = "expired"


class Invite(Base):
    """Приглашение пользователя с контролем ролей и TTL токена."""

    __tablename__ = "invites"
    __table_args__ = (
        Index("ix_invites_token", "token", unique=True),
        Index("ix_invites_status", "status"),
        UniqueConstraint("email", "status", name="uq_invites_email_pending"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    role_requested: Mapped[str] = mapped_column(String(20), nullable=False)
    scope_type: Mapped[InviteScopeType | None] = mapped_column(
        Enum(InviteScopeType, name="invitescopetype", native_enum=True), nullable=True
    )
    scope_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, default=lambda: secrets_token())
    invited_by: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[InviteStatus] = mapped_column(
        Enum(InviteStatus, name="invitestatus", native_enum=True), nullable=False, default=InviteStatus.pending
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=datetime.now
    )

    inviter = relationship("User", lazy="joined")

    def mark_expired(self) -> None:
        """Помечает приглашение истёкшим."""

        if self.status == InviteStatus.pending and datetime.now(timezone.utc) >= self.expires_at:
            self.status = InviteStatus.expired


def secrets_token() -> str:
    """Генерирует короткий токен, удобный для рассылки."""

    return uuid.uuid4().hex


def default_expiry(hours: int = 72) -> datetime:
    """Возвращает дату истечения TTL приглашения."""

    return datetime.now(timezone.utc) + timedelta(hours=hours)


__all__ = ["Invite", "InviteStatus", "InviteScopeType", "default_expiry"]
