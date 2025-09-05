"""Price list schemas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, condecimal, constr

PriceDecimal = condecimal(max_digits=12, decimal_places=2)
CurrencyStr = constr(min_length=3, max_length=3)


class PriceBase(BaseModel):
    price: PriceDecimal
    currency: CurrencyStr = "KZT"
    valid_from: date
    valid_to: date | None = None


class PriceCreate(PriceBase):
    sku_id: str


class PriceUpdate(BaseModel):
    price: PriceDecimal | None = None
    currency: CurrencyStr | None = None
    valid_from: date | None = None
    valid_to: date | None = None


class PriceRead(PriceBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    sku_id: str


class EffectivePriceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sku_id: str
    price: PriceDecimal
    currency: CurrencyStr
    valid_from: date
    valid_to: date | None = None


__all__ = [
    "PriceCreate",
    "PriceUpdate",
    "PriceRead",
    "EffectivePriceRead",
]
