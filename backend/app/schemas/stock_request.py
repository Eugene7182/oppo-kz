# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, conint


class StockRequestStatus(str, Enum):
    new = "new"
    approved = "approved"
    rejected = "rejected"
    fulfilled = "fulfilled"


class StockRequestBase(BaseModel):
    store_id: Optional[int] = Field(None, ge=1)
    sku_id: Optional[int] = Field(None, ge=1)
    memory_option: Optional[str] = Field(None, max_length=50)
    qty: conint(ge=1) = 1
    comment: Optional[str] = None


class StockRequestCreate(StockRequestBase):
    pass


class StockRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    promoter_id: Optional[int] = None
    supervisor_id: Optional[int] = None
    store_id: Optional[int] = None
    sku_id: Optional[int] = None
    memory_option: Optional[str] = None
    qty: int
    comment: Optional[str] = None
    status: StockRequestStatus
    created_at: datetime
    updated_at: datetime
