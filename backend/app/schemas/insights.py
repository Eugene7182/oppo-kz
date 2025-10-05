"""Схемы AI-инсайтов."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class InsightKPI(BaseModel):
    """Основные показатели KPI для генерации инсайтов."""

    name: str = Field(..., description="Название KPI, например 'Выручка'")
    unit: str | None = Field(None, description="Единица измерения (₸, шт и т.д.)")
    plan: float | None = Field(None, description="Плановое значение за период")
    actual: float = Field(..., description="Фактическое значение за период")
    delta: float | None = Field(None, description="Абсолютное отклонение факт-план")
    delta_percent: float | None = Field(None, description="Отклонение в процентах")
    wow_percent: float | None = Field(None, description="Дельта к предыдущей неделе")
    mom_percent: float | None = Field(None, description="Дельта к предыдущему месяцу")
    yoy_percent: float | None = Field(None, description="Дельта к прошлому году")


class InsightPopulation(BaseModel):
    """Сегмент/измерение, на котором сфокусированы изменения."""

    name: str
    value: float | None = None
    delta_percent: float | None = None


class InsightAnomaly(BaseModel):
    """Описание аномалий, найденных алгоритмами."""

    dimension: str = Field(..., description="Измерение, например сеть или регион")
    metric: str = Field(..., description="Метрика, по которой зафиксирована аномалия")
    severity: Literal["low", "medium", "high"] | None = Field(
        None, description="Уровень критичности"
    )
    description: str = Field(..., description="Человекочитаемое описание")


class InsightTopItem(BaseModel):
    """Элемент в топ-списке ростов/падений."""

    name: str
    value: float | None = None
    delta_percent: float | None = None


class InsightTopSummary(BaseModel):
    """Подборка лучших/худших изменений."""

    drops: list[InsightTopItem] = Field(default_factory=list)
    gains: list[InsightTopItem] = Field(default_factory=list)


class InsightSummarizeRequest(BaseModel):
    """Запрос на генерацию саммари по KPI."""

    scope: str = Field(..., examples=["national", "network:Mechta"])
    period: str = Field(..., description="Период в произвольном формате, напр. '2024-09'")
    kpi: InsightKPI
    pops: list[InsightPopulation] = Field(default_factory=list)
    anomalies: list[InsightAnomaly] = Field(default_factory=list)
    tops: InsightTopSummary = Field(default_factory=InsightTopSummary)

    model_config = {
        "json_schema_extra": {
            "example": {
                "scope": "national",
                "period": "2024-09",
                "kpi": {
                    "name": "Выручка",
                    "unit": "₸",
                    "plan": 5200000000,
                    "actual": 4800000000,
                    "wow_percent": -7.2,
                    "mom_percent": -3.5,
                },
                "pops": [
                    {"name": "Сеть A", "delta_percent": -12.0},
                    {"name": "Регион Юг", "delta_percent": -8.1},
                ],
                "anomalies": [
                    {
                        "dimension": "Сеть A",
                        "metric": "Выручка",
                        "severity": "high",
                        "description": "Падение продаж Reno 11 на 25%",
                    }
                ],
                "tops": {
                    "drops": [
                        {"name": "Сеть A", "delta_percent": -12.0},
                        {"name": "Сеть B", "delta_percent": -5.0},
                    ],
                    "gains": [
                        {"name": "Сеть C", "delta_percent": 4.5},
                    ],
                },
            }
        }
    }


class InsightAction(BaseModel):
    """Кнопка действия на фронтенде."""

    label: str = Field(..., description="Текст кнопки")
    action: str = Field(..., description="Идентификатор действия для фронтенда")


class InsightSummary(BaseModel):
    """Ответ AI-инсайтов."""

    headline: str
    bullets: list[str] = Field(default_factory=list)
    actions: list[InsightAction] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "headline": "Выручка просела на 7.7% от плана в период 2024-09.",
                "bullets": [
                    "Факт 4.8 млрд ₸ против плана 5.2 млрд ₸ (-7.7%).",
                    "Динамика: WoW −7.2%, MoM −3.5%.",
                    "Главное падение: Сеть A (−12.0%), прирост: Сеть C (+4.5%).",
                    "Аномалия: Сеть A — Падение продаж Reno 11 на 25%.",
                ],
                "actions": [
                    {"label": "Создать задачу супервизору", "action": "create_supervisor_task"},
                    {"label": "Открыть бонус-сетку", "action": "open_bonus_grid"},
                    {"label": "Отфильтровать по SKU/сети", "action": "open_filters"},
                ],
            }
        }
    }

