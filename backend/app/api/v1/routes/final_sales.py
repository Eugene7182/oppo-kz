# backend/app/api/v1/routes/final_sales.py
from __future__ import annotations

from datetime import date
from io import StringIO
import csv

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ....models import SalesFinal, Store, SKU
from ..deps import get_db, require_super

router = APIRouter()


# ---------- Pydantic схемы ответа ----------
class FinalSalesItem(BaseModel):
    id: int
    date: date
    store_id: int
    store_name: str
    network: str
    sku_id: int
    sku_code: str
    qty: int
    amount: float
    source: str


class FinalSalesList(BaseModel):
    total_qty: int
    total_amount: float
    items: list[FinalSalesItem]


def _base_stmt():
    # Общий SELECT с джоинами для отображения названий
    return (
        select(
            SalesFinal,             # ORM-объект
            Store.name,             # index 1
            Store.network,          # index 2
            SKU.code,               # index 3
        )
        .join(Store, Store.id == SalesFinal.store_id)
        .join(SKU, SKU.id == SalesFinal.sku_id)
    )


def _apply_filters(stmt, date_from: date | None, date_to: date | None,
                   store_id: int | None, network: str | None, sku_code: str | None):
    if date_from:
        stmt = stmt.where(SalesFinal.date >= date_from)
    if date_to:
        stmt = stmt.where(SalesFinal.date <= date_to)
    if store_id:
        stmt = stmt.where(SalesFinal.store_id == store_id)
    if network:
        stmt = stmt.where(Store.network == network)
    if sku_code:
        # точное совпадение кода; при желании можно сделать ilike("%...%")
        stmt = stmt.where(SKU.code == sku_code)
    return stmt


# ---------- ЭНДПОИНТЫ ----------
@router.get("/", response_model=FinalSalesList, dependencies=[Depends(require_super())])
def list_final_sales(
    db: Session = Depends(get_db),
    date_from: date | None = None,
    date_to: date | None = None,
    store_id: int | None = None,
    network: str | None = None,
    sku_code: str | None = None,
):
    """
    Возвращает итоговые продажи (SalesFinal) со справочными названиями и итогами.
    Все параметры — необязательные фильтры.
    """
    stmt = _apply_filters(_base_stmt(), date_from, date_to, store_id, network, sku_code)
    rows = db.execute(stmt).all()

    items: list[FinalSalesItem] = []
    total_qty = 0
    total_amount = 0.0

    for sf, store_name, net, code in rows:
        qty = int(sf.qty or 0)
        amt = float(sf.amount or 0.0)
        total_qty += qty
        total_amount += amt

        items.append(
            FinalSalesItem(
                id=sf.id,
                date=sf.date,
                store_id=sf.store_id,
                store_name=store_name or "",
                network=net or "",
                sku_id=sf.sku_id,
                sku_code=code or "",
                qty=qty,
                amount=amt,
                source=sf.source,
            )
        )

    return FinalSalesList(
        total_qty=total_qty,
        total_amount=total_amount,
        items=items,
    )


@router.get("/export", dependencies=[Depends(require_super())])
def export_final_sales_csv(
    db: Session = Depends(get_db),
    date_from: date | None = None,
    date_to: date | None = None,
    store_id: int | None = None,
    network: str | None = None,
    sku_code: str | None = None,
):
    """
    Экспорт итоговых продаж в CSV.
    Колонки: date, store, network, sku_code, qty, amount, source
    """
    stmt = _apply_filters(_base_stmt(), date_from, date_to, store_id, network, sku_code)
    rows = db.execute(stmt).all()

    buf = StringIO()
    w = csv.writer(buf)
    w.writerow(["date", "store", "network", "sku_code", "qty", "amount", "source"])

    for sf, store_name, net, code in rows:
        w.writerow([
            sf.date.isoformat(),
            store_name or "",
            net or "",
            code or "",
            int(sf.qty or 0),
            float(sf.amount or 0.0),
            sf.source or "",
        ])

    csv_bytes = buf.getvalue()
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="final_sales.csv"'},
    )
