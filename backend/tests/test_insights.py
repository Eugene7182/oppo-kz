"""Тесты эндпоинта AI-инсайтов."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.settings import settings
from app.main import app


def _payload() -> dict[str, object]:
    return {
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


def test_insights_disabled(monkeypatch) -> None:
    monkeypatch.setattr(settings, "feature_ai_insights", False)
    client = TestClient(app)
    response = client.post("/api/v1/insights/summarize", json=_payload())
    assert response.status_code == 404
    assert response.json() == {"detail": "Feature disabled", "code": "feature_disabled"}


def test_insights_rule_based(monkeypatch) -> None:
    monkeypatch.setattr(settings, "feature_ai_insights", True)
    monkeypatch.setattr(settings, "openai_api_key", None)
    client = TestClient(app)
    response = client.post("/api/v1/insights/summarize", json=_payload())
    assert response.status_code == 200
    data = response.json()
    assert data["headline"] == "Выручка просел на 7.7% от плана в период 2024-09."
    assert any("Факт" in bullet for bullet in data["bullets"])
    assert len(data["actions"]) == 3
    assert {action["action"] for action in data["actions"]} == {
        "create_supervisor_task",
        "open_bonus_grid",
        "open_filters",
    }

