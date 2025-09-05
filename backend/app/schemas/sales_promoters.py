from __future__ import annotations

"""Pydantic schemas for promoter sales."""

from datetime import date, datetime, timedelta
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


class PromoterSaleBase(BaseModel):
    store_id: str
    sku_id: str
    qty: int
    amount: Decimal
    sold_at: date

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


class PromoterSaleCreate(PromoterSaleBase):
    promoter_id: str | None = None


class PromoterSaleUpdate(BaseModel):
    qty: int | None = None
    amount: Decimal | None = None

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


class PromoterSaleRead(PromoterSaleBase):
    id: str
    promoter_id: str
    unit_price: Decimal
    approved_by_office: bool
    approved_at: datetime | None = None
    approved_by_user_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "PromoterSaleCreate",
    "PromoterSaleUpdate",
    "PromoterSaleRead",
]
