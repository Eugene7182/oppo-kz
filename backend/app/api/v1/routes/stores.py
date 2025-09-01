# backend/app/api/v1/routes/stores.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ....models import Store
from ....schemas import StoreOut, StoreIn
from ..deps import get_db, require_super

router = APIRouter(prefix="/stores", tags=["stores"])


@router.get("", response_model=list[StoreOut])
def list_stores(db: Session = Depends(get_db)):
    rows = db.scalars(select(Store).order_by(Store.network, Store.city, Store.name)).all()
    return rows


@router.post("", response_model=StoreOut, dependencies=[Depends(require_super())])
def create_store(body: StoreIn, db: Session = Depends(get_db)):
    # уникальность: (name, city, network)
    exists = db.scalar(
        select(Store).where(
            Store.name == body.name.strip(),
            Store.city == (body.city or "").strip(),
            Store.network == (body.network or "").strip(),
        )
    )
    if exists:
        raise HTTPException(status_code=409, detail="Store already exists")

    row = Store(
        name=body.name.strip(),
        city=(body.city or "").strip(),
        network=(body.network or "").strip(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
