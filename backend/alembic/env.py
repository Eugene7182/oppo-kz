from __future__ import annotations

import os
import sys
import importlib
import pkgutil
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# --- Alembic config (alembic.ini) ---
config = context.config

# Подключаем логирование из alembic.ini (если есть)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- PYTHONPATH: добавим корень backend, чтобы работали 'import app.*' ---
# Текущий файл: backend/alembic/env.py → корень backend — на уровень выше
BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

# --- DATABASE_URL: читаем из ENV и прокладываем в alembic config ---
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

# --- Импортируем Base (если получится) ---
Base = None  # type: ignore[assignment]
base_import_error: Exception | None = None

# Популярные варианты местоположения Base в проекте
for base_path in ("app.db.base_class", "app.db.session"):
    try:
        mod = importlib.import_module(base_path)
        Base = getattr(mod, "Base")
        break
    except Exception as e:
        base_import_error = e
        continue

# --- Если Base найден — поднимем все модели из app.models/* ---
target_metadata = None
if Base is not None:
    try:
        import app.models as models_pkg  # пакет с моделями
        # Импортируем все подмодули внутри app.models (user.py, invite.py, ...)
        for _, modname, _ in pkgutil.iter_modules(models_pkg.__path__):
            try:
                importlib.import_module(f"app.models.{modname}")
            except Exception:
                # Не валим процесс миграций: пропустим поломанный модуль
                pass
        target_metadata = Base.metadata  # type: ignore[attr-defined]
    except Exception:
        # Если что-то пошло не так при загрузке моделей — не блокируем миграции
        target_metadata = None
else:
    # Base не найден — миграции из versions/* всё равно применятся,
    # но autogenerate использовать нельзя до починки импортов Base/моделей.
    target_metadata = None

# --- Оффлайн миграции (генерация SQL без подключения к БД) ---
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set, и sqlalchemy.url в alembic.ini не указан."
        )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,  # учитывать изменения типов колонок
    )

    with context.begin_transaction():
        context.run_migrations()

# --- Онлайновые миграции (через подключение к БД) ---
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # учитывать изменения типов колонок
        )

        with context.begin_transaction():
            context.run_migrations()

# --- Точка входа ---
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
