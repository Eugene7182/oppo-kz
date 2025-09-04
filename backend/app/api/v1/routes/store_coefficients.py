from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ....core.security import get_db
from ....models import StoreCoefficient, Store
from ....schemas import StoreCoefficientIn, StoreCoefficientOut
from app.security_rbac import require_roles
router = APIRouter(prefix="/store-coefficients", tags=["store-coefficients"])
@router.get("/", response_model=List[StoreCoefficientOut], dependencies=[Depends(require_roles("admin", "office"))])
def list_coeffs(store_id: Optional[int] = None, code: Optional[str] = None, db: Session = Depends(get_db)):
    q = select(StoreCoefficient)
    if store_id is not None: q = q.where(StoreCoefficient.store_id == store_id)
    if code: q = q.where(StoreCoefficient.code == code)
    return db.scalars(q.order_by(StoreCoefficient.store_id, StoreCoefficient.code, StoreCoefficient.valid_from.desc())).all()
@router.post("/", response_model=StoreCoefficientOut, dependencies=[Depends(require_roles("admin", "office"))])
def create_coeff(body: StoreCoefficientIn, db: Session = Depends(get_db)):
    store = db.get(Store, body.store_id)
    if not store: raise HTTPException(status_code=404, detail="Store not found")
    coeff = StoreCoefficient(store_id=body.store_id, code=body.code.strip(), value=body.value, note=body.note, valid_from=body.valid_from or date.today(), valid_to=body.valid_to)
    db.add(coeff); db.commit(); db.refresh(coeff); return coeff
@router.put("/{coeff_id}", response_model=StoreCoefficientOut, dependencies=[Depends(require_roles("admin", "office"))])
def update_coeff(coeff_id: int, body: StoreCoefficientIn, db: Session = Depends(get_db)):
    coeff = db.get(StoreCoefficient, coeff_id)
    if not coeff: raise HTTPException(status_code=404, detail="Not found")
    coeff.store_id = body.store_id; coeff.code = body.code.strip(); coeff.value = body.value; coeff.note = body.note
    coeff.valid_from = body.valid_from or coeff.valid_from; coeff.valid_to = body.valid_to
    db.add(coeff); db.commit(); db.refresh(coeff); return coeff
@router.delete("/{coeff_id}", status_code=204, dependencies=[Depends(require_roles("admin", "office"))])
def delete_coeff(coeff_id: int, db: Session = Depends(get_db)):
    coeff = db.get(StoreCoefficient, coeff_id)
    if not coeff: raise HTTPException(status_code=404, detail="Not found")
    db.delete(coeff); db.commit(); return None
