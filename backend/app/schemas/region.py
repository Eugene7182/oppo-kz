"""Region schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class RegionBase(BaseModel):
    name: str


class RegionCreate(RegionBase):
    pass


class RegionUpdate(BaseModel):
    name: str


class RegionRead(RegionBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


__all__ = ["RegionCreate", "RegionUpdate", "RegionRead"]
