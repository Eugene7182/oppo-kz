"""Logging configuration.

Логирование в JSON на stdout.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401 - short
        log: Dict[str, Any] = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "method": getattr(record, "method", None),
            "path": getattr(record, "path", None),
            "status": getattr(record, "status", None),
            "duration_ms": getattr(record, "duration_ms", None),
            "user_id": getattr(record, "user_id", None),
            "trace_id": getattr(record, "trace_id", None),
        }
        extra = getattr(record, "extra", None)
        if isinstance(extra, dict):
            log.update(extra)
        return json.dumps(log, ensure_ascii=False)


def setup_logging() -> None:
    """Configure root logger to use JSON formatter."""

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.INFO)
    root.addHandler(handler)

