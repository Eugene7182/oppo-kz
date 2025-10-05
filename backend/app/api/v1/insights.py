"""Маршруты AI-инсайтов."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.settings import settings
from app.feature_flags.deps import check_feature
from app.schemas.insights import InsightSummarizeRequest, InsightSummary
from app.services.insights import InsightsService

router = APIRouter()


def get_insights_service() -> InsightsService:
    """Возвращает сервис с текущими настройками."""

    return InsightsService(settings)


@router.post(
    "/summarize",
    response_model=InsightSummary,
    dependencies=[Depends(check_feature("FEATURE_AI_INSIGHTS"))],
    summary="Генерация AI-саммари по KPI",
)
async def summarize_insights(
    body: InsightSummarizeRequest,
    service: InsightsService = Depends(get_insights_service),
) -> InsightSummary:
    """Возвращает структурированный саммари и действия."""

    return await service.summarize(body)


__all__ = ["router"]

