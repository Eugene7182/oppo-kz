from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
from datetime import date
from app.api.v1.deps import get_db, get_current_user, require_promoter_or_supervisor

router = APIRouter(prefix="/sales", tags=["sales"])

def _has(db, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

def _is_current_month(d: str) -> bool:
    try:
        dt = date.fromisoformat(d)
        today = date.today()
        return dt.year == today.year and dt.month == today.month
    except Exception:
        return False

def _stores_for_supervisor(db: Session, username: str):
    if not _has(db, "stores"): return set()
    rows = db.execute(text("select store_id from stores where supervisor_name=:u"), {"u": username}).mappings().all()
    return {r["store_id"] for r in rows}

@router.get("/list")
def list_sales(d: str = Query(..., alias="date"), store_id: str | None = None, promoter_username: str | None = None,
               db: Session = Depends(get_db), user = Depends(get_current_user), _: None = Depends(require_promoter_or_supervisor)):
    if not _has(db, "sales_daily"): return {"rows": []}
    if not _is_current_month(d): raise HTTPException(status_code=400, detail="Only current month is editable")
    role = getattr(user, "role", None)
    params = {"d": d}
    cond = "where date=:d"
    if store_id:
        cond += " and store_id=:st"; params["st"] = store_id
    if promoter_username:
        cond += " and coalesce(promoter,'')=:p"; params["p"] = promoter_username
    else:
        if role == "promoter":
            cond += " and coalesce(promoter,'')=:p"; params["p"] = getattr(user, "username", "")
        elif role == "supervisor":
            stores = _stores_for_supervisor(db, getattr(user, "username", ""))
            if not stores:
                return {"rows": []}
            cond += " and store_id = any(:stores)"; params["stores"] = list(stores)
    rows = db.execute(text(f"""
        select date, store_id, sku_id, model, memory_gb, qty, revenue, network_id, coalesce(promoter,'') as promoter
        from sales_daily {cond}
        order by store_id, sku_id, coalesce(memory_gb,-1)
    """), params).mappings().all()
    return {"rows": [dict(r) for r in rows]}

@router.put("/upsert")
def upsert_sale(payload: dict, db: Session = Depends(get_db), user = Depends(get_current_user), _: None = Depends(require_promoter_or_supervisor)):
    if not _has(db, "sales_daily"): raise HTTPException(status_code=503, detail="sales_daily missing")
    d = payload.get("date")
    if not d or not _is_current_month(d):
        raise HTTPException(status_code=400, detail="date (current month) required")
    store_id = payload.get("store_id")
    sku_id = payload.get("sku_id")
    memory_gb = payload.get("memory_gb")
    qty = int(payload.get("qty") or 0)
    price = payload.get("price_per_unit")
    revenue = None if price is None else float(price) * qty
    model = payload.get("model")
    network_id = payload.get("network_id")
    promoter_param = payload.get("promoter_username")
    role = getattr(user, "role", None)
    if not store_id or not sku_id:
        raise HTTPException(status_code=400, detail="store_id and sku_id required")

    # permissions
    if role == "promoter":
        promoter = getattr(user, "username", "")
        if promoter_param and promoter_param != promoter:
            raise HTTPException(status_code=403, detail="Cannot edit others' sales")
    elif role == "supervisor":
        stores = _stores_for_supervisor(db, getattr(user, "username", ""))
        if store_id not in stores:
            raise HTTPException(status_code=403, detail="Store not supervised")
    promoter_val = promoter_param if promoter_param is not None else (getattr(user, "username", "") if role == "promoter" else "")

    # absolute set (not incremental): replace existing qty/revenue
    db.execute(text("""
        insert into sales_daily(date, store_id, sku_id, model, memory_gb, qty, revenue, network_id, promoter)
        values (:d,:st,:sku,:m,:mem,:q,:rev,:net,:p)
        on conflict (date, store_id, sku_id, coalesce(memory_gb, -1), coalesce(promoter,''))
        do update set qty=:q, revenue=:rev, model=excluded.model, network_id=excluded.network_id
    """), {"d": d, "st": store_id, "sku": sku_id, "m": model, "mem": memory_gb, "q": qty, "rev": revenue, "net": network_id, "p": promoter_val})
    db.commit()
    db.execute(text("insert into audit_log(event_type, actor, meta) values ('sales_upsert', :a, :m)"), {'a': getattr(user,'username',None), 'm': json_build_object(:d,:st,:sku,:mem,:q)} );
    return {"ok": True}

@router.delete("")
def delete_sale(d: str = Query(..., alias="date"), store_id: str = Query(...), sku_id: str = Query(...), memory_gb: int | None = Query(None),
                promoter_username: str | None = Query(None), db: Session = Depends(get_db), user = Depends(get_current_user), _: None = Depends(require_promoter_or_supervisor)):
    if not _has(db, "sales_daily"): raise HTTPException(status_code=503, detail="sales_daily missing")
    if not _is_current_month(d): raise HTTPException(status_code=400, detail="Only current month is editable")
    role = getattr(user, "role", None)
    if role == "promoter":
        promoter = getattr(user, "username", "")
        if promoter_username and promoter_username != promoter:
            raise HTTPException(status_code=403, detail="Cannot delete others' sales")
        promoter_username = promoter
    elif role == "supervisor":
        stores = _stores_for_supervisor(db, getattr(user, "username", ""))
        if store_id not in stores:
            raise HTTPException(status_code=403, detail="Store not supervised")
    db.execute(text("""
        delete from sales_daily where date=:d and store_id=:st and sku_id=:sku
          and coalesce(memory_gb,-1)=coalesce(:mem,-1) and coalesce(promoter,'')=coalesce(:p,'')
    """), {"d": d, "st": store_id, "sku": sku_id, "mem": memory_gb, "p": promoter_username or ""})
    db.commit()
    db.execute(text("insert into audit_log(event_type, actor, meta) values ('sales_upsert', :a, :m)"), {'a': getattr(user,'username',None), 'm': json_build_object(:d,:st,:sku,:mem,:q)} );
    return {"ok": True}
