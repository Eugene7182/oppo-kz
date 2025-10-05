"""Sales and related audit models."""
from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


def utcnow() -> datetime:
    """Возвращает время в UTC для колонок."""

    return datetime.now(timezone.utc)


class SaleStatus(str, enum.Enum):
    """Статусы продажи."""

    active = "active"
    deleted = "deleted"


class Sale(Base):
    """Продажа промоутера с версионированием и блокировками."""

    __tablename__ = "sales"
    __table_args__ = (
        CheckConstraint("qty >= 0", name="ck_sales_qty_non_negative"),
        CheckConstraint("price >= 0", name="ck_sales_price_non_negative"),
        Index("ix_sales_promoter_date", "promoter_id", "date"),
        Index("ix_sales_store_date", "store_id", "date"),
        UniqueConstraint("id", name="uq_sales_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    promoter_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id", ondelete="RESTRICT"), nullable=False)
    sku_id: Mapped[str] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    status: Mapped[SaleStatus] = mapped_column(
        Enum(SaleStatus, name="salestatus", native_enum=True), default=SaleStatus.active, nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    promoter = relationship("User")
    store = relationship("Store")
    sku = relationship("Product")
    revisions = relationship("SaleRevision", back_populates="sale", cascade="all, delete-orphan")
    corrections = relationship("SaleCorrection", back_populates="sale", cascade="all, delete-orphan")


class SaleRevision(Base):
    """История изменений продажи."""

    __tablename__ = "sale_revisions"
    __table_args__ = (Index("ix_sale_revisions_sale_id", "sale_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sale_id: Mapped[str] = mapped_column(ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    changed_by: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    before_json: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    after_json: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    sale = relationship("Sale", back_populates="revisions")


class SaleCorrection(Base):
    """Коррекция продажи в закрытом периоде."""

    __tablename__ = "sale_corrections"
    __table_args__ = (Index("ix_sale_corrections_sale_id", "sale_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sale_id: Mapped[str] = mapped_column(ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    delta_qty: Mapped[int] = mapped_column(Integer, nullable=False)
    delta_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    sale = relationship("Sale", back_populates="corrections")


__all__ = ["Sale", "SaleRevision", "SaleCorrection", "SaleStatus"]
