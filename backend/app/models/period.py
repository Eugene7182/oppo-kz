"""Closed periods tracking."""
from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.sale import utcnow


class ClosedScope(str, enum.Enum):
    """Тип охвата закрытого периода."""

    country = "country"
    region = "region"
    store = "store"


class ClosedPeriod(Base):
    """Закрытый период продаж."""

    __tablename__ = "closed_periods"
    __table_args__ = (Index("ix_closed_period_scope", "scope", "scope_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scope: Mapped[ClosedScope] = mapped_column(
        Enum(ClosedScope, name="closedscope", native_enum=True), nullable=False
    )
    scope_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    from_date: Mapped[date] = mapped_column(Date, nullable=False)
    to_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


__all__ = ["ClosedPeriod", "ClosedScope"]
