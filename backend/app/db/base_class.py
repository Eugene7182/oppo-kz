# Re-export Base from app.models so that models importing from app.db.base_class work.
from app.models import Base

__all__ = ["Base"]
