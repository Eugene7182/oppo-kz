
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.inventory import StockBalance

def list_balances(db: Session, store_id: int | None = None, sku_id: int | None = None):
    q = select(StockBalance)
    if store_id: q = q.where(StockBalance.store_id == store_id)
    if sku_id: q = q.where(StockBalance.sku_id == sku_id)
    return db.execute(q).scalars().all()

def upsert_balance(db: Session, *, store_id: int, sku_id: int, on_hand: float, in_transit: float):
    row = db.query(StockBalance).filter_by(store_id=store_id, sku_id=sku_id).first()
    if row:
        row.on_hand = float(on_hand); row.in_transit = float(in_transit)
    else:
        row = StockBalance(store_id=store_id, sku_id=sku_id, on_hand=float(on_hand), in_transit=float(in_transit))
        db.add(row); db.flush()
    return row

def delete_balance(db: Session, id: int):
    row = db.get(StockBalance, id)
    if not row: return False
    db.delete(row); return True
