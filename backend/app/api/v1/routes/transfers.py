from fastapi import APIRouter, Depends, Query
from typing import Optional, List, Dict, Any
from ....core.security import get_current_user
router = APIRouter(prefix="/transfers", tags=["transfers"])

@router.get("/suggest")
def suggest_transfers(store: str, horizon: int = 14, safety: int = 7, user=Depends(get_current_user)):
    # Heuristic: static mock suggesting to pull from WH1
    return [{
        "sku": "OPPO-A1K",
        "from": "WH1",
        "to": store,
        "qty": 12,
        "reason": f"forecast_gap (h={horizon}, safety={safety})"
    }]


from pydantic import BaseModel
from typing import List

class TransferItem(BaseModel):
    sku: str
    from_store: str
    to_store: str
    qty: int

@router.post("/apply")
def apply_transfers(items: List[TransferItem], user=Depends(get_current_user)):
    # MVP: просто возвращаем подтверждённый список
    return {"accepted": len(items), "items": [i.dict() for i in items]}
