from __future__ import annotations

"""Price list model."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Index, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class PriceList(Base):
    """Цена SKU с периодом действия."""

    __tablename__ = "price_list"
    __table_args__ = (
        Index("ix_pricelist_sku_valid_from_desc", "sku_id", text("valid_from DESC")),
        Index("ix_pricelist_sku_valid_to", "sku_id", "valid_to"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sku_id: Mapped[str] = mapped_column(ForeignKey("sku.id", ondelete="RESTRICT"), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="KZT")
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    sku = relationship("Sku", back_populates="prices")


__all__ = ["PriceList"]
