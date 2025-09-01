from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class StockRequestCreate(BaseModel):
    store_id: Optional[int] = None
    sku_id: Optional[int] = None
    memory_option: Optional[str] = None
    qty: int = 1
    comment: Optional[str] = None

class StockRequestOut(BaseModel):
    id: int
    promoter_id: Optional[int]
    supervisor_id: Optional[int]
    store_id: Optional[int]
    sku_id: Optional[int]
    memory_option: Optional[str]
    qty: int
    comment: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    class Config: from_attributes = True
