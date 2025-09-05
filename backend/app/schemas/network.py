"""Network schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class NetworkBase(BaseModel):
    name: str


class NetworkCreate(NetworkBase):
    pass


class NetworkUpdate(BaseModel):
    name: str


class NetworkRead(NetworkBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


__all__ = ["NetworkCreate", "NetworkUpdate", "NetworkRead"]
