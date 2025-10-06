"""Analytics computations for BI widgets."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.sale import Sale, SaleCorrection, SaleStatus


@dataclass(slots=True)
class RangeAggregates:
    """Aggregated sales metrics for a period."""

    base_qty: int
    base_revenue: Decimal
    correction_qty: int
    correction_revenue: Decimal

    @property
    def fact_qty(self) -> int:
        return self.base_qty + self.correction_qty

    @property
    def fact_revenue(self) -> Decimal:
        return self.base_revenue + self.correction_revenue


def _to_decimal(value: object | None) -> Decimal:
    if value is None:
        return Decimal(0)
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def month_add(value: date, offset: int) -> date:
    month = value.month - 1 + offset
    year = value.year + month // 12
    month = month % 12 + 1
    day = min(value.day, _monthrange(year, month))
    return date(year, month, day)


def month_start(value: date) -> date:
    return value.replace(day=1)


def month_end(value: date) -> date:
    return month_add(month_start(value), 1) - timedelta(days=1)


def _monthrange(year: int, month: int) -> int:
    import calendar

    return calendar.monthrange(year, month)[1]


class SalesAnalyticsService:
    """Сервис агрегирования продаж."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _stores_in_range(self, start: date, end: date) -> list[str]:
        stmt = (
            select(Sale.store_id)
            .where(
                Sale.date >= start,
                Sale.date <= end,
                Sale.status == SaleStatus.active,
            )
            .distinct()
        )
        return list(self.session.execute(stmt).scalars())

    def _aggregate(self, start: date, end: date, store_ids: Sequence[str] | None = None) -> RangeAggregates:
        query = self.session.query(
            func.coalesce(func.sum(Sale.qty), 0),
            func.coalesce(func.sum(Sale.qty * func.coalesce(Sale.price, 0)), 0),
        ).filter(Sale.date >= start, Sale.date <= end, Sale.status == SaleStatus.active)
        if store_ids:
            query = query.filter(Sale.store_id.in_(store_ids))
        base_qty, base_revenue = query.one()

        corr_query = (
            self.session.query(
                func.coalesce(func.sum(SaleCorrection.delta_qty), 0),
                func.coalesce(func.sum(SaleCorrection.delta_price), 0),
            )
            .join(Sale, SaleCorrection.sale_id == Sale.id)
            .filter(Sale.date >= start, Sale.date <= end)
        )
        if store_ids:
            corr_query = corr_query.filter(Sale.store_id.in_(store_ids))
        corr_qty, corr_revenue = corr_query.one()
        return RangeAggregates(
            base_qty=int(base_qty or 0),
            base_revenue=_to_decimal(base_revenue),
            correction_qty=int(corr_qty or 0),
            correction_revenue=_to_decimal(corr_revenue),
        )

    def _period_value(self, agg: RangeAggregates) -> dict[str, Decimal | int]:
        return {"qty": agg.fact_qty, "revenue": agg.fact_revenue}

    def _delta(self, current: RangeAggregates | None, previous: RangeAggregates | None) -> tuple[dict[str, Decimal | int] | None, dict[str, Decimal | int] | None, Decimal | None]:
        current_payload = self._period_value(current) if current else None
        previous_payload = self._period_value(previous) if previous else None
        change = None
        if current_payload and previous_payload and previous_payload["revenue"]:
            change = ((current_payload["revenue"] - previous_payload["revenue"]) / previous_payload["revenue"]) * Decimal(100)
        return current_payload, previous_payload, change

    def compute(self, as_of: date) -> dict[str, object]:
        """Посчитать метрики на заданную дату."""

        today = as_of
        month_start_current = month_start(today)
        mtd = self._aggregate(month_start_current, today)
        stores = self._stores_in_range(month_start_current, today)

        last_year_start = month_add(month_start_current, -12)
        last_year_end = month_add(today, -12)
        lfl = self._aggregate(last_year_start, last_year_end, stores) if stores else RangeAggregates(0, Decimal(0), 0, Decimal(0))

        current_week_start = today - timedelta(days=today.weekday())
        last_week_start = current_week_start - timedelta(days=7)
        last_week_end = current_week_start - timedelta(days=1)
        prev_week_start = last_week_start - timedelta(days=7)
        prev_week_end = last_week_start - timedelta(days=1)
        week_current = self._aggregate(last_week_start, last_week_end)
        week_previous = self._aggregate(prev_week_start, prev_week_end)

        prev_month_start = month_add(month_start_current, -1)
        prev_month_end = month_end(prev_month_start)
        two_months_ago_start = month_add(prev_month_start, -1)
        two_months_ago_end = month_end(two_months_ago_start)
        month_current = self._aggregate(prev_month_start, prev_month_end)
        month_previous = self._aggregate(two_months_ago_start, two_months_ago_end)

        prev_month_last_year_start = month_add(prev_month_start, -12)
        prev_month_last_year_end = month_end(prev_month_last_year_start)
        yoy_prev = self._aggregate(prev_month_last_year_start, prev_month_last_year_end)

        current_payload, previous_payload, wow_change = self._delta(week_current, week_previous)
        mom_current, mom_previous, mom_change = self._delta(month_current, month_previous)
        yoy_current, yoy_previous, yoy_change = self._delta(month_current, yoy_prev)
        lfl_current, lfl_previous, lfl_change = self._delta(mtd, lfl)

        return {
            "as_of": today,
            "mtd": {
                "base_qty": mtd.base_qty,
                "base_revenue": mtd.base_revenue,
                "correction_qty": mtd.correction_qty,
                "correction_revenue": mtd.correction_revenue,
                "fact_qty": mtd.fact_qty,
                "fact_revenue": mtd.fact_revenue,
            },
            "mtd_lfl": {
                "current": lfl_current,
                "previous": lfl_previous,
                "change_pct": lfl_change,
            },
            "wow": {
                "current": current_payload,
                "previous": previous_payload,
                "change_pct": wow_change,
            },
            "mom": {
                "current": mom_current,
                "previous": mom_previous,
                "change_pct": mom_change,
            },
            "yoy": {
                "current": yoy_current,
                "previous": yoy_previous,
                "change_pct": yoy_change,
            },
        }
