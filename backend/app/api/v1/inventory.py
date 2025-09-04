
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, require_roles
from app.services.inventory import list_balances, upsert_balance, delete_balance

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.get("")
def list_(store_id: int | None = None, sku_id: int | None = None, db: Session = Depends(get_db), _=Depends(require_roles("admin","office","supervisor"))):
    rows = list_balances(db, store_id, sku_id)
    return {"items": [dict(id=r.id, store_id=r.store_id, sku_id=r.sku_id, on_hand=r.on_hand, in_transit=r.in_transit) for r in rows]}

@router.post("/upsert")
def upsert(data: dict, db: Session = Depends(get_db), _=Depends(require_roles("admin","office"))):
    try:
        row = upsert_balance(db, store_id=int(data["store_id"]), sku_id=int(data["sku_id"]), on_hand=float(data["on_hand"]), in_transit=float(data.get("in_transit") or 0))
        return {"id": row.id}
    except KeyError as e:
        raise HTTPException(400, f"missing: {e}")

@router.delete("/{id}")
def delete(id: int, db: Session = Depends(get_db), _=Depends(require_roles("admin","office"))):
    ok = delete_balance(db, id)
    if not ok: raise HTTPException(404, "not found")
    return {"ok": True}
