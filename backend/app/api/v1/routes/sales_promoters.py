# backend/app/api/v1/routes/sales_promoters.py
from __future__ import annotations

from datetime import date
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
import pandas as pd
from pydantic import BaseModel, Field

from ....models import SalesPromoter, PriceList
from ....schemas import UploadResult
from ..deps import get_db, require_super, require_promoter_or_super

router = APIRouter(prefix="/sales/promoters", tags=["sales-promoters"])


# ===== helpers =====
def _read_frame(file: UploadFile) -> pd.DataFrame:
    name = (file.filename or "").lower()
    if name.endswith(".csv"):
        return pd.read_csv(file.file)
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(file.file)
    raise HTTPException(status_code=400, detail="Only CSV or Excel files are supported")


def _active_price(db: Session, sku_id: int, on: date) -> float | None:
    stmt = (
        select(PriceList)
        .where(
            and_(
                PriceList.sku_id == sku_id,
                PriceList.valid_from <= on,
                (PriceList.valid_to.is_(None)) | (PriceList.valid_to >= on),
            )
        )
        .order_by(PriceList.valid_from.desc())
    )
    row = db.scalars(stmt).first()
    if not row:
        return None
    return float(row.price or 0)


# ===== CSV/XLSX upload (для супервайзера) =====
@router.post("/upload", response_model=UploadResult, dependencies=[Depends(require_super())])
def upload_promoters(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = _read_frame(file)

    required = {"date", "store_id", "sku_id", "qty"}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing)}")

    inserted = 0
    skipped = 0
    errors: list[str] = []

    for idx, row in df.iterrows():
        try:
            sold_at = pd.to_datetime(row["date"]).date()
            qty = int(row["qty"])
            amount = float(row["amount"]) if "amount" in df.columns and pd.notna(row["amount"]) else None

            if amount is None:
                ap = _active_price(db, int(row["sku_id"]), sold_at)
                amount = float(ap * qty) if ap is not None else 0.0

            sp = SalesPromoter(
                store_id=int(row["store_id"]),
                sku_id=int(row["sku_id"]),
                qty=qty,
                amount=amount,
                sold_at=sold_at,
                promoter=str(row["promoter"]) if "promoter" in df.columns and pd.notna(row["promoter"]) else "",
            )
            db.add(sp)
            inserted += 1
        except Exception as e:
            skipped += 1
            errors.append(f"row {idx+1}: {e}")

    db.commit()
    return UploadResult(rows_total=int(inserted + skipped), rows_inserted=int(inserted), rows_skipped=int(skipped), errors=errors)


# ===== ОДНА продажа (для промоутера/супера) =====
class PromoterSaleIn(BaseModel):
    date: date
    store_id: int
    sku_id: int
    qty: int = Field(ge=1)
    amount: float | None = None  # если не передали — посчитаем по прайсу

@router.post("/add", dependencies=[Depends(require_promoter_or_super())])
def add_promoter_sale(body: PromoterSaleIn, db: Session = Depends(get_db)):
    amount = body.amount
    if amount is None:
        ap = _active_price(db, body.sku_id, body.date)
        amount = float((ap or 0) * body.qty)

    sp = SalesPromoter(
        store_id=body.store_id,
        sku_id=body.sku_id,
        qty=body.qty,
        amount=amount,
        sold_at=body.date,
        promoter="",  # можно подставлять current.username, если хочешь — скажи, добавлю
    )
    db.add(sp)
    db.commit()
    return {"ok": True, "id": sp.id, "amount": float(amount or 0)}
