"""Product catalog model with SKU lifecycle states."""
from __future__ import annotations

import enum
import uuid

from sqlalchemy import DateTime, Enum, Index, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON

from app.db.base_class import Base


class ProductStatus(str, enum.Enum):
    """Статусы SKU."""

    active = "active"
    eol = "eol"
    archived = "archived"


class Product(Base):
    """SKU с дополнительными атрибутами."""

    __tablename__ = "products"
    __table_args__ = (Index("ix_products_sku", "sku", unique=True),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sku: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus, name="productstatus", native_enum=True), default=ProductStatus.active, nullable=False
    )
    attrs_json: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )
    valid_from: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_to: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    price: Mapped[Numeric | None] = mapped_column(Numeric(12, 2), nullable=True)


__all__ = ["Product", "ProductStatus"]
