# backend/alembic/env.py
from __future__ import annotations
import os
import sys
import pkgutil
import importlib
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Подтягиваем конфиг Alembic
config = context.config

# Если alembic.ini указан, применим его логирование
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- PYTHONPATH и URL БД ---
# Убедимся, что корень backend в sys.path
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

# Берём URL из ENV (Render -> Environment -> DATABASE_URL)
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

# --- Metadata ---
# Пробуем импортировать Base
Base = None
try:
    # частый случай: Base объявлен в app.db.session
    from app.db.session import Base as SessionBase  # type: ignore
    Base = SessionBase
except Exception:
    try:
        from app.db.base_class import Base as BaseClass  # type: ignore
        Base = BaseClass
    except Exception as e:
        raise RuntimeError(f"Cannot import SQLAlchemy Base: {e}")

# Динамически импортируем все модели, чтобы таблицы попали в metadata
try:
    import app.models as models_pkg  # пакет с моделями
    for _, modname, _ in pkgutil.iter_modules(models_pkg.__path__):
        try:
            importlib.import_module(f"app.models.{modname}")
        except Exception as e:
            # Не валим миграции, просто лог внутри Alembic будет
            pass
except Exception:
    # Если нет пакета models — ok, возможно модели импортируются иначе
    pass

target_metadata = Base.metadata  # type: ignore

def run_migrations_offline() -> None:
    """Запуск в offline-режиме."""
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,  # полезно для изменений типов
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Запуск в online-режиме."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
