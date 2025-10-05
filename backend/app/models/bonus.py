"""Bonus schemes and rules."""
from __future__ import annotations

import enum
import uuid

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
)
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.sale import utcnow


class BonusSchemeStatus(str, enum.Enum):
    """Статус бонусной схемы."""

    draft = "draft"
    published = "published"


class BonusScheme(Base):
    """Схема бонусов сети."""

    __tablename__ = "bonus_schemes"
    __table_args__ = (Index("ix_bonus_schemes_network", "network_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    network_id: Mapped[str] = mapped_column(ForeignKey("networks.id", ondelete="CASCADE"), nullable=False)
    valid_from: Mapped[Date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[Date | None] = mapped_column(Date, nullable=True)
    status: Mapped[BonusSchemeStatus] = mapped_column(
        Enum(BonusSchemeStatus, name="bonusschemestatus", native_enum=True), default=BonusSchemeStatus.draft
    )
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    rules = relationship("BonusRule", back_populates="scheme", cascade="all, delete-orphan")


class BonusSelectorType(str, enum.Enum):
    """Вид селектора правила."""

    sku = "sku"
    series = "series"
    all = "all"


class BonusRule(Base):
    """Правило расчёта бонуса."""

    __tablename__ = "bonus_rules"
    __table_args__ = (Index("ix_bonus_rules_scheme", "scheme_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scheme_id: Mapped[str] = mapped_column(ForeignKey("bonus_schemes.id", ondelete="CASCADE"), nullable=False)
    selector_type: Mapped[BonusSelectorType] = mapped_column(
        Enum(BonusSelectorType, name="bonusselectortype", native_enum=True), nullable=False
    )
    selector_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    conditions_json: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)

    scheme = relationship("BonusScheme", back_populates="rules")


__all__ = ["BonusScheme", "BonusRule", "BonusSchemeStatus", "BonusSelectorType"]
