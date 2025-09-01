from fastapi import APIRouter, Depends
from ....core.security import get_current_user
from datetime import date, timedelta

router = APIRouter(prefix="/forecast", tags=["forecast"])

@router.get("/sku/{code}")
def forecast_sku(code: str, store: str | None = None, period: int = 30, user=Depends(get_current_user)):
    # MVP: линейный тренд + шум
    today = date.today()
    out = []
    base = 10 if code.endswith("A1K") else 5
    for i in range(period):
        day = (today + timedelta(days=i)).isoformat()
        out.append({"date": day, "sku": code, "store": store, "forecast": base + i // 7})
    return out
