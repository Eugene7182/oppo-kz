"""Feature flag helpers.

Флаги читаются из ENV через объект настроек.
"""

from __future__ import annotations

from app.core.settings import settings


class Flags:
    """Access boolean feature flags from settings."""

    @property
    def ENABLE_BONUSES(self) -> bool:  # включение бонусов
        return settings.enable_bonuses

    @property
    def ENABLE_MESSAGES(self) -> bool:  # включение сообщений
        return settings.enable_messages

    @property
    def ENABLE_IMPORTS(self) -> bool:  # включение загрузок
        return settings.enable_imports

    @property
    def ENABLE_ANALYTICS(self) -> bool:  # включение аналитики
        return settings.enable_analytics


flags = Flags()


__all__ = ["flags", "Flags"]

