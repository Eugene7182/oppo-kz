"""Feature flag dependencies.

Использовать как dependency или декоратор: ``Depends(check_feature("FLAG"))``.
"""

from __future__ import annotations

from typing import Callable

from app.feature_flags.flags import flags


class FeatureDisabled(Exception):
    """Raised when a feature is disabled."""

    def __init__(self, feature: str):
        self.feature = feature
        super().__init__(feature)


def check_feature(name: str) -> Callable[[], None]:
    """Return FastAPI dependency checking a feature flag."""

    def dependency() -> None:
        if not getattr(flags, name, False):
            raise FeatureDisabled(name)

    return dependency


__all__ = ["check_feature", "FeatureDisabled"]

