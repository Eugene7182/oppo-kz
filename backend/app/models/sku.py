from __future__ import annotations

"""SKU model."""

import uuid

from sqlalchemy import Boolean, Index, String, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Sku(Base):
    """Товарная позиция (SKU)."""

    __tablename__ = "sku"
    __table_args__ = (
        Index("ix_sku_brand", "brand"),
        Index("ix_sku_model", "model"),
        Index("ix_sku_active", "active"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    attrs: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    prices = relationship("PriceList", back_populates="sku", cascade="all, delete-orphan")


__all__ = ["Sku"]
