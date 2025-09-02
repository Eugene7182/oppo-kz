m ....models import BonusPayout
# backend/app/schemas/__init__.py
from __future__ import annotations

"""
Динамический ре-экспорт ВСЕХ pydantic-моделей из подпакета schemas.
Любой роут, который делает: `from app.schemas import XYZ`, — теперь не упадёт,
даже если XYZ находится в отдельном файле.
"""

import importlib
import inspect
import pkgutil
from pydantic import BaseModel

__all__: list[str] = []

# Проходим по всем модулям в пакете app.schemas
for _finder, _name, _ispkg in pkgutil.iter_modules(__path__):  # type: ignore[name-defined]
    if _name.startswith("_") or _name == "__pycache__":
        continue
    try:
        mod = importlib.import_module(f"{__name__}.{_name}")
    except Exception:
        # Не валимся, если какой-то модуль кривой — просто пропускаем
        continue
    # Экспортируем все классы Pydantic-моделей
    for attr, obj in vars(mod).items():
        try:
            if inspect.isclass(obj) and issubclass(obj, BaseModel) and obj is not BaseModel:
                globals()[attr] = obj
                __all__.append(attr)
        except Exception:
            # На случай динамических объектов и пр.
            continue
            
# Provide lowercase alias for StoreCoefficientOut for backward compatibility
try:
    from .store_coefficients import StoreCoefficientOut
    storeCoefficientOut = StoreCoefficientOut  # alias for older imports
    __all__.append("storeCoefficientOut")
except ImportError:
 
# Provide aliases for BonusCalc models and backward compatibility
try:
    from app.core_schemas import (
        BonusCalcPreviewIn,
        BonusCalcPreviewOut,
        BonusCommitIn,
        BonusCalcItem,
        BonusPayoutOut,
    )
    # Export classes to schemas namespace
    BonusCalcPreviewIn = BonusCalcPreviewIn  # type: ignore  # noqa
    BonusCalcPreviewOut = BonusCalcPreviewOut  # type: ignore  # noqa
    BonusCalcPrevewOut = BonusCalcPreviewOut  # alias for misspelling
    BonusCommitIn = BonusCommitIn  # type: ignore  # noqa
    BonusCalcItem = BonusCalcItem  # type: ignore  # noqa
    BonusPayoutOut = BonusPayoutOut  # type: ignore  # noqa

    __all__.extend([
        "BonusCalcPreviewIn",
        "BonusCalcPreviewOut",
        "BonusCalcPrevewOut",
        "BonusCommitIn",
        "BonusCalcItem",
        "BonusPayoutOut",
    ])
except ImportError:
    pass
   pass

