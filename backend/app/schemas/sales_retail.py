from __future__ import annotations

"""Pydantic schemas for retail sales."""

from datetime import date, datetime, timedelta
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


class RetailSaleBase(BaseModel):
    store_id: str
    sku_id: str
    qty: int
    amount: Decimal
    sold_at: date
    external_id: str | None = None
    feed_batch_id: str | None = None

    @field_validator("qty")
    @classmethod
    def _qty_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("qty must be > 0")
        return v

    @field_validator("amount")
    @classmethod
    def _amount_non_negative(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("amount must be >= 0")
        return v

    @field_validator("sold_at")
    @classmethod
    def _sold_not_future(cls, v: date) -> date:
        if v > date.today() + timedelta(days=1):
            raise ValueError("sold_at too far in future")
        return v


class RetailSaleCreate(RetailSaleBase):
    pass


class RetailSaleUpdate(BaseModel):
    qty: int | None = None
    amount: Decimal | None = None
    sold_at: date | None = None

    @field_validator("qty")
    @classmethod
    def _qty_positive(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("qty must be > 0")
        return v

    @field_validator("amount")
    @classmethod
    def _amount_non_negative(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v < 0:
            raise ValueError("amount must be >= 0")
        return v

    @field_validator("sold_at")
    @classmethod
    def _sold_not_future(cls, v: date | None) -> date | None:
        if v is not None and v > date.today() + timedelta(days=1):
            raise ValueError("sold_at too far in future")
        return v


class RetailSaleRead(RetailSaleBase):
    id: str
    unit_price: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RetailSalesImport(BaseModel):
    items: list[RetailSaleCreate]


__all__ = [
    "RetailSaleCreate",
    "RetailSaleUpdate",
    "RetailSaleRead",
    "RetailSalesImport",
]
