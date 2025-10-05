"""Сервис генерации AI-инсайтов."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Iterable

import httpx

from app.core.settings import Settings
from app.schemas.insights import (
    InsightAction,
    InsightAnomaly,
    InsightPopulation,
    InsightSummarizeRequest,
    InsightSummary,
    InsightTopItem,
)

_LOGGER = logging.getLogger(__name__)

_PROMPT = (
    "You are a retail analytics assistant. Given strictly the JSON metrics below (plan vs actual, WoW/MoM/YoY deltas, "
    "anomalies, top drops/gains), write a concise 2–4 sentence summary in Russian and propose 1–3 concrete actions. Do not "
    "invent entities not present in input. Output JSON with fields: headline, bullets[], actions[]. <INPUT_JSON>"
)


@dataclass(slots=True)
class _RuleBasedContext:
    payload: InsightSummarizeRequest
    plan_gap_pct: float | None
    dominant_drop: InsightTopItem | None
    dominant_gain: InsightTopItem | None


class InsightsService:
    """Инкапсулирует режимы rule-based и LLM."""

    def __init__(self, settings: Settings):
        self._settings = settings

    async def summarize(self, payload: InsightSummarizeRequest) -> InsightSummary:
        """Возвращает саммари по KPI."""

        if self._settings.openai_api_key:
            try:
                return await self._summarize_with_llm(payload)
            except Exception as exc:  # noqa: BLE001
                _LOGGER.exception("LLM insights failed, fallback to rule-based: %s", exc)
        return self._summarize_rule_based(payload)

    # ------------------------------------------------------------------
    # Rule-based
    # ------------------------------------------------------------------
    def _summarize_rule_based(self, payload: InsightSummarizeRequest) -> InsightSummary:
        ctx = _RuleBasedContext(
            payload=payload,
            plan_gap_pct=self._calc_plan_gap_pct(payload),
            dominant_drop=(payload.tops.drops[0] if payload.tops.drops else None),
            dominant_gain=(payload.tops.gains[0] if payload.tops.gains else None),
        )

        headline = self._make_headline(ctx)
        bullets = self._make_bullets(ctx)
        actions = self._make_actions(ctx)

        return InsightSummary(headline=headline, bullets=bullets, actions=actions)

    def _calc_plan_gap_pct(self, payload: InsightSummarizeRequest) -> float | None:
        plan = payload.kpi.plan
        if plan in (None, 0):
            return None
        actual = payload.kpi.actual
        if plan == 0:
            return None
        return ((actual - plan) / plan) * 100

    def _make_headline(self, ctx: _RuleBasedContext) -> str:
        name = ctx.payload.kpi.name
        period = ctx.payload.period
        gap = ctx.plan_gap_pct
        if gap is not None and abs(gap) >= 2:
            if gap < 0:
                return f"{name} просел на {self._format_percent(abs(gap), signed=False)} от плана в период {period}."
            return f"{name} перевыполнен на {self._format_percent(gap)} относительно плана за {period}."
        trend = self._first_defined(
            ctx.payload.kpi.delta_percent,
            ctx.payload.kpi.wow_percent,
            ctx.payload.kpi.mom_percent,
            ctx.payload.kpi.yoy_percent,
        )
        if trend is not None:
            sign = "растёт" if trend >= 0 else "снижается"
            return f"{name} {sign} на {self._format_percent(abs(trend), signed=False)} за период {period}."
        return f"{name}: ключевые наблюдения за {period}."

    def _make_bullets(self, ctx: _RuleBasedContext) -> list[str]:
        bullets: list[str] = []
        kpi = ctx.payload.kpi
        unit = kpi.unit or ""
        if kpi.plan is not None:
            plan_text = self._format_amount(kpi.plan, unit)
            actual_text = self._format_amount(kpi.actual, unit)
            gap_text = (
                f" ({self._format_percent(ctx.plan_gap_pct)})"
                if ctx.plan_gap_pct is not None
                else ""
            )
            bullets.append(f"Факт {actual_text} против плана {plan_text}{gap_text}.")
        else:
            actual_text = self._format_amount(kpi.actual, unit)
            bullets.append(f"Факт {actual_text} без заданного плана.")

        trends: list[str] = []
        if kpi.wow_percent is not None:
            trends.append(f"WoW {self._format_percent(kpi.wow_percent)}")
        if kpi.mom_percent is not None:
            trends.append(f"MoM {self._format_percent(kpi.mom_percent)}")
        if kpi.yoy_percent is not None:
            trends.append(f"YoY {self._format_percent(kpi.yoy_percent)}")
        if trends:
            bullets.append(f"Динамика: {', '.join(trends)}.")

        focus_segments = [
            f"{pop.name} ({self._format_percent(pop.delta_percent)})"
            for pop in ctx.payload.pops[:3]
            if pop.delta_percent is not None
        ]
        if focus_segments:
            bullets.append("Фокус сегменты: " + ", ".join(focus_segments) + ".")

        if ctx.dominant_drop or ctx.dominant_gain:
            if ctx.dominant_drop and ctx.dominant_drop.delta_percent is not None:
                bullets.append(
                    f"Главное падение: {ctx.dominant_drop.name} ({self._format_percent(ctx.dominant_drop.delta_percent)})."
                )
            if ctx.dominant_gain and ctx.dominant_gain.delta_percent is not None:
                bullets.append(
                    f"Прирост: {ctx.dominant_gain.name} ({self._format_percent(ctx.dominant_gain.delta_percent)})."
                )

        for anomaly in ctx.payload.anomalies[:2]:
            bullets.append(
                f"Аномалия: {anomaly.dimension} — {anomaly.description}."
            )

        return bullets

    def _make_actions(self, ctx: _RuleBasedContext) -> list[InsightAction]:
        return [
            InsightAction(label="Создать задачу супервизору", action="create_supervisor_task"),
            InsightAction(label="Открыть бонус-сетку", action="open_bonus_grid"),
            InsightAction(label="Отфильтровать по SKU/сети", action="open_filters"),
        ]

    # ------------------------------------------------------------------
    # LLM mode
    # ------------------------------------------------------------------
    async def _summarize_with_llm(self, payload: InsightSummarizeRequest) -> InsightSummary:
        body = payload.model_dump(exclude_none=True)
        prompt = _PROMPT.replace("<INPUT_JSON>", json.dumps(body, ensure_ascii=False))
        headers = {
            "Authorization": f"Bearer {self._settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self._settings.openai_model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "user", "content": prompt},
            ],
        }
        async with httpx.AsyncClient(base_url=self._settings.openai_base_url.rstrip("/"), timeout=30.0) as client:
            response = await client.post("/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        payload_json = response.json()
        try:
            message = payload_json["choices"][0]["message"]["content"]
            parsed = json.loads(message)
        except (KeyError, ValueError, IndexError) as exc:  # noqa: PERF203
            raise RuntimeError("Unexpected OpenAI response") from exc
        return InsightSummary.model_validate(parsed)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _format_amount(self, value: float, unit: str | None) -> str:
        scaled_value = value
        suffix = ""
        abs_value = abs(value)
        if abs_value >= 1_000_000_000:
            scaled_value = value / 1_000_000_000
            suffix = " млрд"
        elif abs_value >= 1_000_000:
            scaled_value = value / 1_000_000
            suffix = " млн"
        formatted = f"{scaled_value:.1f}".rstrip("0").rstrip(".")
        unit_part = f" {unit}" if unit else ""
        return f"{formatted}{suffix}{unit_part}".strip()

    def _format_percent(self, value: float | None, *, signed: bool = True) -> str:
        if value is None:
            return "0%"
        magnitude = abs(value)
        if not signed or magnitude == 0:
            return f"{magnitude:.1f}%"
        sign = "+" if value > 0 else ("-" if value < 0 else "")
        return f"{sign}{magnitude:.1f}%"

    def _first_defined(self, *values: float | None) -> float | None:
        for value in values:
            if value is None:
                continue
            return value
        return None


__all__ = ["InsightsService"]

