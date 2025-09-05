from __future__ import annotations

"""Sales entries loaded from retail networks."""

import uuid
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import text

from app.db.base_class import Base


class SalesRetail(Base):
    """Продажа, загруженная из сети."""

    __tablename__ = "sales_retail"
    __table_args__ = (
        CheckConstraint("qty > 0", name="ck_sales_retail_qty_positive"),
        CheckConstraint("amount >= 0", name="ck_sales_retail_amount_non_negative"),
        Index("ix_sales_retail_store_id_sold_at", "store_id", "sold_at"),
        Index("ix_sales_retail_sku_id_sold_at", "sku_id", "sold_at"),
        Index("ix_sales_retail_feed_batch_id", "feed_batch_id"),
        Index(
            "ux_sales_retail_external_id",
            "external_id",
            unique=True,
            postgresql_where=text("external_id IS NOT NULL"),
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id", ondelete="RESTRICT"), nullable=False)
    sku_id: Mapped[str] = mapped_column(ForeignKey("sku.id", ondelete="RESTRICT"), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    sold_at: Mapped[date] = mapped_column(Date, nullable=False)
    feed_batch_id: Mapped[str | None] = mapped_column(String, nullable=True)
    external_id: Mapped[str | None] = mapped_column(String, nullable=True)

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


__all__ = ["SalesRetail"]
