from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, timedelta
from app.api.v1.deps import get_db, get_current_user, require_office_or_supervisor_or_admin as require_power

router = APIRouter(prefix="/bonus", tags=["bonus"])

def _has(db, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

@router.get("/networks")
def list_networks(db: Session = Depends(get_db), _: None = Depends(require_power)):
    rows = db.execute(text("select distinct network_id from stores where network_id is not null order by 1")).mappings().all() if _has(db, "stores") else []
    return {"networks": [r["network_id"] for r in rows]}

@router.get("/grid")
def get_grid(network_id: str = Query(...), month: str | None = Query(None),
             db: Session = Depends(get_db), _: None = Depends(require_power)):
    rows = []
    if not _has(db, "skus"):
        return {"items": []}
    if month and _has(db, "network_phone_bonus_hist"):
        rows = db.execute(text("""
            with sel as (
              select sku_id, amount
              from network_phone_bonus_hist
              where network_id=:n and valid_from <= :m and (valid_to is null or valid_to >= :m)
              order by valid_from desc
            )
            select s.sku_id, s.display_name as model, coalesce((select amount from sel where sel.sku_id=s.sku_id),0) as amount
            from skus s
            order by s.display_name
        """), {"n": network_id, "m": month}).mappings().all()
    elif _has(db, "network_phone_bonus"):
        rows = db.execute(text("""
            select s.sku_id, s.display_name as model, coalesce(b.amount,0) as amount
            from skus s left join network_phone_bonus b on b.sku_id = s.sku_id and b.network_id = :n
            order by s.display_name
        """), {"n": network_id}).mappings().all()
    else:
        rows = db.execute(text("select sku_id, display_name as model, 0 as amount from skus order by display_name")).mappings().all()
    return {"items": [dict(r) for r in rows]}

@router.post("/grid")
def upsert_grid(payload: dict, db: Session = Depends(get_db), user = Depends(get_current_user), _: None = Depends(require_power)):
    role = getattr(user, "role", None)
    if role == "supervisor":
        raise HTTPException(status_code=403, detail="Only admin/office can edit bonus grids")
    network_id = payload.get("network_id")
    items = payload.get("items", [])
    month = payload.get("month")  # YYYY-MM-01
    if not network_id or not isinstance(items, list):
        raise HTTPException(status_code=400, detail="network_id and items[] required")
    if not _has(db, "network_phone_bonus_hist"):
        raise HTTPException(status_code=503, detail="bonus history table missing")
    if not month:
        month = date.today().replace(day=1).isoformat()
    prev_end = (date.fromisoformat(month) - timedelta(days=1)).isoformat()
    db.execute(text("""
        update network_phone_bonus_hist
        set valid_to = :prev_end
        where network_id=:n and valid_to is null and valid_from < :m
    """), {"n": network_id, "m": month, "prev_end": prev_end})
    for it in items:
        sku = it.get("sku_id"); amount = float(it.get("amount") or 0)
        db.execute(text("""
            insert into network_phone_bonus_hist(network_id, sku_id, amount, valid_from)
            values (:n,:s,:a,:m)
        """), {"n": network_id, "s": sku, "a": amount, "m": month})
    db.commit()
    # audit
    if _has(db, "audit_log"):
        db.execute(text("insert into audit_log(event_type, actor, meta) values ('bonus_grid_upsert', :a, :m)"),
                   {"a": getattr(user,'username',None), "m": {"network_id": network_id, "month": month, "items_count": len(items)}})
        db.commit()
    return {"ok": True, "network_id": network_id, "month": month, "updated": len(items)}
