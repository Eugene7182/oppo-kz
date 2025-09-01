from fastapi import APIRouter,UploadFile,File,HTTPException
import csv,io,datetime
from app.services.validators import validate_row
from ....db import SessionLocal   # было "....db.session"
from ....models import Sale,Stock,Plan
router=APIRouter(prefix='/upload')

def _parse_csv(file:UploadFile):
  raw=file.file.read().decode('utf-8-sig')
  reader=csv.DictReader(io.StringIO(raw))
  rows=list(reader)
  if not rows: raise HTTPException(400,'empty file')
  return rows

@router.post('/sales')
def upload_sales(file:UploadFile=File(...)):
  rows=_parse_csv(file); db=SessionLocal(); ok=0; fail=0
  for r in rows:
    try:
      validate_row('SalesReport.schema.json',r)
      obj=Sale(report_date=datetime.date.fromisoformat(r['report_date']),network_id=r['network_id'],store_id=r['store_id'],promoter_id=r['promoter_id'],brand=r['brand'],model=r['model'],qty=int(r['qty']),price=float(r['price']),currency=r.get('currency','KZT'))
      db.add(obj); ok+=1
    except Exception: fail+=1
  db.commit(); return {'ok':ok,'failed':fail}

@router.post('/stock')
def upload_stock(file:UploadFile=File(...)):
  rows=_parse_csv(file); db=SessionLocal(); ok=0; fail=0
  for r in rows:
    try:
      validate_row('StockReport.schema.json',r)
      obj=Stock(report_date=datetime.date.fromisoformat(r['report_date']),network_id=r['network_id'],store_id=r['store_id'],brand=r['brand'],model=r['model'],stock_qty=int(r['stock_qty']),incoming_qty=int(r.get('incoming_qty',0)),outgoing_qty=int(r.get('outgoing_qty',0)))
      db.add(obj); ok+=1
    except Exception: fail+=1
  db.commit(); return {'ok':ok,'failed':fail}

@router.post('/plan')
def upload_plan(file:UploadFile=File(...)):
  rows=_parse_csv(file); db=SessionLocal(); ok=0; fail=0
  for r in rows:
    try:
      validate_row('Plan.schema.json',r)
      obj=Plan(period=r['period'],network_id=r['network_id'],store_id=(r.get('store_id') or None),brand=(r.get('brand') or None),model=(r.get('model') or None),target_qty=int(r['target_qty']))
      db.add(obj); ok+=1
    except Exception: fail+=1
  db.commit(); return {'ok':ok,'failed':fail}
