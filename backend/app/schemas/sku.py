"""SKU schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SkuBase(BaseModel):
    brand: str
    model: str
    attrs: dict | None = None
    active: bool | None = True


class SkuCreate(SkuBase):
    pass


class SkuUpdate(BaseModel):
    brand: str | None = None
    model: str | None = None
    attrs: dict | None = None
    active: bool | None = None


class SkuRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    brand: str
    model: str
    attrs: dict | None = None
    active: bool


__all__ = ["SkuCreate", "SkuUpdate", "SkuRead"]
