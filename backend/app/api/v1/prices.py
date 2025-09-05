from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_current_user, rbac_required
from app.db.session import get_db
from app.models.price import PriceList
from app.models.sku import Sku
from app.models.user import UserRole
from app.schemas.price import (
    EffectivePriceRead,
    PriceCreate,
    PriceRead,
    PriceUpdate,
)
from app.services.price_service import (
    PriceOverlapError,
    ensure_no_overlap,
    get_effective_price,
    get_effective_prices,
)
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("", dependencies=[Depends(get_current_user)], response_model=dict)
def list_prices(
    limit: int = 100,
    offset: int = 0,
    sku_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
) -> dict:
    """Список цен с фильтрами."""
    stmt = select(PriceList)
    if sku_id:
        stmt = stmt.where(PriceList.sku_id == sku_id)
    if date_from:
        stmt = stmt.where(PriceList.valid_from >= date_from)
    if date_to:
        stmt = stmt.where(or_(PriceList.valid_to == None, PriceList.valid_to <= date_to))
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(PriceList.valid_from.desc()).offset(offset).limit(limit)).all()
    items = [PriceRead.model_validate(r) for r in rows]
    return {"items": items, "total": total}


_admin_office = rbac_required([UserRole.admin, UserRole.office])


@router.post("", dependencies=[Depends(_admin_office)], response_model=PriceRead, status_code=status.HTTP_201_CREATED)
def create_price_endpoint(data: PriceCreate, db: Session = Depends(get_db)) -> PriceList:
    """Создать цену."""
    if not db.get(Sku, data.sku_id):
        raise HTTPException(status_code=400, detail={"detail": "Sku not found", "code": "sku_not_found"})
    try:
        ensure_no_overlap(db, data.sku_id, data.valid_from, data.valid_to)
    except PriceOverlapError as exc:
        return JSONResponse(
            status_code=400,
            content={"code": "price_overlap", "detail": str(exc)},
        )
    price = PriceList(
        sku_id=data.sku_id,
        price=data.price,
        currency=data.currency,
        valid_from=data.valid_from,
        valid_to=data.valid_to,
    )
    db.add(price)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return JSONResponse(
            status_code=400,
            content={"code": "price_overlap", "detail": "Price period overlaps"},
        )
    db.refresh(price)
    return price


@router.put("/{price_id}", dependencies=[Depends(_admin_office)], response_model=PriceRead)
def update_price_endpoint(price_id: str, data: PriceUpdate, db: Session = Depends(get_db)) -> PriceList:
    """Обновить цену."""
    price = db.get(PriceList, price_id)
    if not price:
        raise HTTPException(status_code=404, detail={"detail": "Price not found", "code": "price_not_found"})
    new_valid_from = data.valid_from or price.valid_from
    new_valid_to = data.valid_to if data.valid_to is not None else price.valid_to
    try:
        ensure_no_overlap(db, price.sku_id, new_valid_from, new_valid_to, exclude_id=price.id)
    except PriceOverlapError as exc:
        return JSONResponse(
            status_code=400,
            content={"code": "price_overlap", "detail": str(exc)},
        )
    if data.price is not None:
        price.price = data.price
    if data.currency is not None:
        price.currency = data.currency
    if data.valid_from is not None:
        price.valid_from = data.valid_from
    if data.valid_to is not None:
        price.valid_to = data.valid_to
    db.add(price)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return JSONResponse(
            status_code=400,
            content={"code": "price_overlap", "detail": "Price period overlaps"},
        )
    db.refresh(price)
    return price


@router.delete("/{price_id}", dependencies=[Depends(_admin_office)], response_model=PriceRead)
def delete_price_endpoint(price_id: str, db: Session = Depends(get_db)) -> PriceList:
    """Удалить цену."""
    price = db.get(PriceList, price_id)
    if not price:
        raise HTTPException(status_code=404, detail={"detail": "Price not found", "code": "price_not_found"})
    db.delete(price)
    db.commit()
    return price


@router.get(
    "/effective",
    dependencies=[Depends(get_current_user)],
    response_model=EffectivePriceRead | list[EffectivePriceRead],
)
def effective_price_endpoint(date: date, sku_id: str | None = None, db: Session = Depends(get_db)):
    """Получить эффективную цену на дату."""
    if sku_id:
        price = get_effective_price(db, date, sku_id)
        if not price:
            raise HTTPException(status_code=404, detail={"detail": "Price not found", "code": "price_not_found"})
        return EffectivePriceRead.model_validate(price)
    prices = get_effective_prices(db, date)
    return [EffectivePriceRead.model_validate(p) for p in prices]


__all__ = ["router"]
