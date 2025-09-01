from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.v1.deps import get_db, require_office_or_supervisor_or_admin as require_power

router = APIRouter(prefix="/skus", tags=["skus"])

def _has(db, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

@router.get("")
def list_skus(db: Session = Depends(get_db)):
    if not _has(db, "skus"):
        return {"items": []}
    rows = db.execute(text("select sku_id, display_name as model from skus order by display_name")).mappings().all()
    return {"items": [dict(r) for r in rows]}

@router.post("")
def add_sku(payload: dict, db: Session = Depends(get_db), _: None = Depends(require_power)):
    sku_id = payload.get("sku_id")
    model = payload.get("model") or payload.get("display_name")
    display = payload.get("display_name") or model
    if not sku_id or not display:
        raise HTTPException(status_code=400, detail="sku_id and display_name required")
    db.execute(text("insert into skus(sku_id, model, display_name) values (:i,:m,:d) on conflict (sku_id) do update set model=:m, display_name=:d"),
               {"i": sku_id, "m": model, "d": display})
    db.commit()
    return {"ok": True}
