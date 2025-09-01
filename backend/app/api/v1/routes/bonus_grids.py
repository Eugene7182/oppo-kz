from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from ....db import get_db
from ....models import BonusGrid
from ....schemas import BonusGridIn, BonusGridOut
from ..deps import require_super  # только супер может изменять

router = APIRouter(prefix="/api/v1/bonus", tags=["Bonus Grids"])

def _active_filter(on: Optional[date]):
    if not on:
        return True
    return and_(BonusGrid.valid_from <= on, (BonusGrid.valid_to.is_(None)) | (BonusGrid.valid_to >= on))

@router.get("/", response_model=List[BonusGridOut])
def list_bonus_grids(
    db: Session = Depends(get_db),
    network: Optional[str] = Query(default=None),
    sku_id: Optional[int] = Query(default=None),
    active_on: Optional[date] = Query(default=None),
):
    stmt = select(BonusGrid).where(_active_filter(active_on))
    if network:
        stmt = stmt.where(BonusGrid.network == network)
    if sku_id:
        stmt = stmt.where(BonusGrid.sku_id == sku_id)
    res = db.execute(stmt.order_by(BonusGrid.valid_from.desc(), BonusGrid.id.desc())).scalars().all()
    return res

@router.post("/", response_model=BonusGridOut, status_code=status.HTTP_201_CREATED)
def create_bonus_grid(
    body: BonusGridIn,
    db: Session = Depends(get_db),
    _super=Depends(require_super),
):
    if not body.sku_id and not body.network:
        raise HTTPException(status_code=400, detail="Укажите sku_id или network")
    obj = BonusGrid(
        sku_id=body.sku_id,
        network=body.network,
        qty_from=body.qty_from or 1,
        bonus_per_unit=body.bonus_per_unit,
        valid_from=body.valid_from,
        valid_to=body.valid_to,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/{grid_id}", response_model=BonusGridOut)
def update_bonus_grid(
    grid_id: int,
    body: BonusGridIn,
    db: Session = Depends(get_db),
    _super=Depends(require_super),
):
    obj = db.get(BonusGrid, grid_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Не найдено")
    if not body.sku_id and not body.network:
        raise HTTPException(status_code=400, detail="Укажите sku_id или network")

    obj.sku_id = body.sku_id
    obj.network = body.network
    obj.qty_from = body.qty_from or 1
    obj.bonus_per_unit = body.bonus_per_unit
    obj.valid_from = body.valid_from
    obj.valid_to = body.valid_to

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{grid_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bonus_grid(
    grid_id: int,
    db: Session = Depends(get_db),
    _super=Depends(require_super),
):
    obj = db.get(BonusGrid, grid_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(obj)
    db.commit()
    return None
