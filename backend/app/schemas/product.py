"""Product API schemas."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.product import ProductStatus


class ProductOut(BaseModel):
    """DTO продукта."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    sku: str
    name: str | None
    status: ProductStatus
    price: Decimal | None
    attrs_json: dict[str, Any] | None = Field(default=None, alias="attrs")
    valid_from: datetime | None
    valid_to: datetime | None


class ProductUpdate(BaseModel):
    """Патч SKU."""

    status: ProductStatus | None = None
    name: str | None = None
    price: Decimal | None = Field(default=None, ge=0)
    valid_to: datetime | None = None


__all__ = ["ProductOut", "ProductUpdate"]
