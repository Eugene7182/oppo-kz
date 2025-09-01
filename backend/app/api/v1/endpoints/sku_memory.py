from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.v1.deps import get_db, require_office_or_supervisor_or_admin as require_power

router = APIRouter(prefix="/skus/memory", tags=["skus"])

def _has(db, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

@router.get("")
def list_memory(sku_id: str = Query(...), db: Session = Depends(get_db)):
    if not _has(db, "sku_memory_options"):
        return {"items": []}
    rows = db.execute(text("select memory_gb from sku_memory_options where sku_id=:i order by memory_gb"), {"i": sku_id}).mappings().all()
    return {"items": [r["memory_gb"] for r in rows]}

@router.post("")
def upsert_memory(payload: dict, db: Session = Depends(get_db), _: None = Depends(require_power)):
    if not _has(db, "sku_memory_options"):
        raise HTTPException(status_code=503, detail="sku_memory_options missing")
    sku_id = payload.get("sku_id")
    options = payload.get("memory_options", [])
    if not sku_id or not isinstance(options, list):
        raise HTTPException(status_code=400, detail="sku_id and memory_options[] required")
    db.execute(text("delete from sku_memory_options where sku_id=:i"), {"i": sku_id})
    for mem in options:
        db.execute(text("insert into sku_memory_options(sku_id, memory_gb) values (:i,:m) on conflict do nothing"), {"i": sku_id, "m": int(mem)})
    db.commit()
    return {"ok": True, "sku_id": sku_id, "count": len(options)}
