from __future__ import annotations

"""Sales entries reported by promoters."""

import uuid
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class SalesPromoter(Base):
    """Продажа, введённая промоутером."""

    __tablename__ = "sales_promoters"
    __table_args__ = (
        CheckConstraint("qty > 0", name="ck_sales_promoters_qty_positive"),
        CheckConstraint("amount >= 0", name="ck_sales_promoters_amount_non_negative"),
        Index("ix_sales_promoters_store_id_sold_at", "store_id", "sold_at"),
        Index("ix_sales_promoters_sku_id_sold_at", "sku_id", "sold_at"),
        Index("ix_sales_promoters_promoter_id_sold_at", "promoter_id", "sold_at"),
        Index("ix_sales_promoters_approved", "approved_by_office"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id", ondelete="RESTRICT"), nullable=False)
    sku_id: Mapped[str] = mapped_column(ForeignKey("sku.id", ondelete="RESTRICT"), nullable=False)
    promoter_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    sold_at: Mapped[date] = mapped_column(Date, nullable=False)

    approved_by_office: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    @hybrid_property
    def unit_price(self) -> Decimal:
        """Цена за единицу (amount/qty)."""
        if not self.qty:
            return Decimal("0")
        return (self.amount / self.qty).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


__all__ = ["SalesPromoter"]
