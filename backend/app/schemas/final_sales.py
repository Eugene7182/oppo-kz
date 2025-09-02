from __future__ import annotations
from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict

class FinalSaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")
    id: str
    store_id: Optional[str] = None
    sku_id: Optional[str] = None
    qty: Optional[float] = None
    amount: Optional[float] = None
    date: Optional[date] = None
