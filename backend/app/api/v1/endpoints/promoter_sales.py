from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date
from app.api.v1.deps import get_db, get_current_user, require_promoter

router = APIRouter(prefix="/promoter/sales", tags=["promoter"])

def _has(db, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

@router.post("")
def add_sale(payload: dict, db: Session = Depends(get_db), user = Depends(get_current_user), _: None = Depends(require_promoter)):
    if not _has(db, "sales_daily"): raise HTTPException(status_code=503, detail="sales_daily missing")
    d = payload.get("date") or date.today().isoformat()
    store_id = payload.get("store_id")
    sku_id = payload.get("sku_id")
    memory_gb = payload.get("memory_gb")  # optional
    qty = int(payload.get("qty") or 0)
    price = float(payload.get("price_per_unit") or 0)
    model = payload.get("model")
    network_id = payload.get("network_id")
    if not store_id or not sku_id or qty <= 0:
        raise HTTPException(status_code=400, detail="store_id, sku_id, qty>0 required")

    # upsert into sales_daily (aggregate)
    db.execute(text("""
        insert into sales_daily(date, store_id, sku_id, model, memory_gb, qty, revenue, network_id, promoter)
        values (:d,:st,:sku,:m,:mem,:q,:rev,:net,:p)
        on conflict (date, store_id, sku_id, coalesce(memory_gb, -1), coalesce(promoter,''))
        do update set qty = sales_daily.qty + EXCLUDED.qty, revenue = coalesce(sales_daily.revenue,0) + EXCLUDED.revenue
    """), {
        "d": d, "st": store_id, "sku": sku_id, "m": model, "mem": memory_gb,
        "q": qty, "rev": qty*price if price>0 else None, "net": network_id, "p": getattr(user, "username", None)
    })
    # mark check-in has_sales
    if _has(db, "promoter_daily_checkins"):
        db.execute(text("""
            insert into promoter_daily_checkins(promoter, date, has_sales)
            values (:p, :d, true)
            on conflict (promoter, date) do update set has_sales=true
        """), {"p": getattr(user, "username", None), "d": d})
    db.commit()
    return {"ok": True}

@router.post("/zero-day")
def zero_day(payload: dict, db: Session = Depends(get_db), user = Depends(get_current_user), _: None = Depends(require_promoter)):
    if not _has(db, "promoter_daily_checkins"): raise HTTPException(status_code=503, detail="checkins missing")
    d = payload.get("date") or date.today().isoformat()
    db.execute(text("""
        insert into promoter_daily_checkins(promoter, date, has_sales)
        values (:p, :d, false)
        on conflict (promoter, date) do update set has_sales=excluded.has_sales
    """), {"p": getattr(user, "username", None), "d": d})
    db.commit()
    return {"ok": True}
