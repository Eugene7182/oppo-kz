
import csv, io
from datetime import date
from sqlalchemy.orm import Session
from app.models.sales import SalesNetwork, SalesPromoter
from app.models.store import Store
from app.models.sku import Sku

def list_network(db: Session, page: int, size: int):
    q = db.query(SalesNetwork)
    total = q.count()
    items = q.order_by(SalesNetwork.sold_at.desc()).limit(size).offset((page-1)*size).all()
    return items, total

def list_promoters(db: Session, page: int, size: int):
    q = db.query(SalesPromoter)
    total = q.count()
    items = q.order_by(SalesPromoter.sold_at.desc()).limit(size).offset((page-1)*size).all()
    return items, total

def import_sales_csv(db: Session, csv_bytes: bytes, source: str, dry_run: bool = True, progress_cb=None):
    reader = csv.DictReader(io.StringIO(csv_bytes.decode('utf-8-sig')))
    required = {'sold_at','store','sku','qty'}
    errors, rows = [], []
    line_no = 1
    for row in reader:
        line_no += 1
        header_set = {k.strip().lower() for k in row.keys()}
        if not required.issubset(header_set):
            return {"ok": False, "error": "CSV header must contain sold_at,store,sku,qty"}
        sold_at = (row.get('sold_at','') or '').strip()
        store = (row.get('store','') or '').strip()
        sku = (row.get('sku','') or '').strip()
        qty = (row.get('qty','') or '').strip()
        try:
            qty_i = int(qty)
        except:
            errors.append(f"Line {line_no}: qty invalid"); continue
        if not sold_at or not store or not sku:
            errors.append(f"Line {line_no}: missing fields"); continue
        rows.append((sold_at, store, sku, qty_i))
    store_map = {s.name: s.id for s in db.query(Store).all()}
    sku_map = {s.code: s.id for s in db.query(Sku).all()}
    for i,(sold_at, store, sku, qty_i) in enumerate(rows, start=2):
        if store not in store_map: errors.append(f"Line {i}: store '{store}' not found")
        if sku not in sku_map: errors.append(f"Line {i}: sku '{sku}' not found")
    if errors: return {"ok": False, "dry_run": dry_run, "errors": errors[:100]}
    if dry_run: return {"ok": True, "dry_run": True, "count": len(rows)}
    Model = SalesNetwork if source == "network" else SalesPromoter
    done = 0
    for (sold_at, store, sku, qty_i) in rows:
        obj = Model(sold_at=date.fromisoformat(sold_at), store_id=store_map[store], sku_id=sku_map[sku], qty=qty_i)
        db.add(obj); done += 1
        if progress_cb and done % 100 == 0: progress_cb(done)
    if progress_cb: progress_cb(done)
    return {"ok": True, "dry_run": False, "inserted": done}
