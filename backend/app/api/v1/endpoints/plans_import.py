from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
import csv, io
from app.api.v1.deps import get_db, require_office_or_supervisor_or_admin as require_power, get_current_user

router = APIRouter(prefix="/plans", tags=["plans"])

def _has(db, tbl: str) -> bool:
    return bool(db.execute(text("select to_regclass(:t) is not null"), {"t": tbl}).scalar())

@router.post("/import")
async def import_plans(file: UploadFile = File(...), month: str = Form(...), db: Session = Depends(get_db), user = Depends(get_current_user), _: None = Depends(require_power)):
    if not _has(db, "plans_store_month"):
        raise HTTPException(status_code=503, detail="plans_store_month missing")
    content = await file.read()
    try:
        txt = content.decode('utf-8-sig')
    except Exception:
        txt = content.decode('utf-8', errors='ignore')
    reader = csv.DictReader(io.StringIO(txt))
    required = {"store_id", "plan_qty"}
    if not required.issubset(set([c.strip() for c in reader.fieldnames or []])):
        raise HTTPException(status_code=400, detail="CSV must contain columns: store_id, plan_qty")
    cnt = 0
    for row in reader:
        store_id = str(row.get("store_id") or "").strip()
        plan_qty = int(float(row.get("plan_qty") or 0))
        if not store_id: 
            continue
        db.execute(text("""
            insert into plans_store_month(store_id, month, plan_qty, created_by)
            values (:s, :m, :q, :u)
            on conflict (store_id, month) do update set plan_qty=:q, updated_at=now()
        """), {"s": store_id, "m": month, "q": plan_qty, "u": getattr(user, "username", None)})
        cnt += 1
    db.commit()
    return {"ok": True, "imported": cnt, "month": month}
