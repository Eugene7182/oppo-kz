# backend/app/api/v1/routes/sales_networks.py
from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
import pandas as pd

from ....models import SalesNetwork
from ....schemas import UploadResult
from ..deps import get_db, require_super

router = APIRouter(prefix="/sales/networks", tags=["sales-networks"])


def _read_frame(file: UploadFile) -> pd.DataFrame:
    name = (file.filename or "").lower()
    if name.endswith(".csv"):
        return pd.read_csv(file.file)
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(file.file)
    raise HTTPException(status_code=400, detail="Only CSV or Excel files are supported")


@router.post("/upload", response_model=UploadResult, dependencies=[Depends(require_super())])
def upload_networks(file: UploadFile = File(...), db: Session = Depends(get_db)):
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
            sn = SalesNetwork(
                store_id=int(row["store_id"]),
                sku_id=int(row["sku_id"]),
                qty=int(row["qty"]),
                amount=float(row["amount"]) if "amount" in df.columns and pd.notna(row["amount"]) else 0,
                sold_at=sold_at,
                source_doc=str(row["source_doc"]) if "source_doc" in df.columns and pd.notna(row["source_doc"]) else "",
            )
            db.add(sn)
            inserted += 1
        except Exception as e:
            skipped += 1
            errors.append(f"row {idx+1}: {e}")

    db.commit()
    return UploadResult(rows_total=int(inserted + skipped), rows_inserted=int(inserted), rows_skipped=int(skipped), errors=errors)
