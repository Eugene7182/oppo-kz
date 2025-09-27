# backend/app/main.py
# -------------------
# FastAPI-приложение для OPPO KZ с авто-ремонтом схемы БД на старте и сидированием администратора.
# Совместимо с Render.com (uvicorn app.main:app)

import os
from datetime import datetime, timedelta
from typing import Generator, Optional
import uuid

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, inspect
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

# Локальные импорты проекта
from app.api.v1.api import api_router
from app.core.security import get_password_hash
from app.db.session import SessionLocal, engine
from app.db.base_class import Base
from app.db.models.user import User

# -----------------------------------------------------------------------------
# Конфигурация из ENV
# -----------------------------------------------------------------------------
PROJECT_NAME = "OPPO KZ API"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
ADMIN_EMAIL = os.getenv("ADMIN_USERNAME", os.getenv("ADMIN_EMAIL", "admin@example.com"))
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")
JWT_SECRET = os.getenv("JWT_SECRET", "change_me_long_random")

# -----------------------------------------------------------------------------
# Утилиты
# -----------------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------------------------------------------------------
# Базовые операции с БД
# -----------------------------------------------------------------------------
def create_all() -> None:
    """
    Создаёт базовые таблицы из моделей (если ещё не существуют).
    """
    Base.metadata.create_all(bind=engine)
    print("INFO:app.main:create_all completed")


def _column_exists(schema: str, table: str, column: str) -> bool:
    if engine.dialect.name != "postgresql":
        return False
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = :schema
                  AND table_name = :table
                  AND column_name = :column
                """
            ),
            {"schema": schema, "table": table, "column": column},
        ).fetchone()
        return bool(row)


def _get_column_type(schema: str, table: str, column: str) -> Optional[str]:
    if engine.dialect.name != "postgresql":
        return None
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT data_type
                FROM information_schema.columns
                WHERE table_schema = :schema
                  AND table_name = :table
                  AND column_name = :column
                """
            ),
            {"schema": schema, "table": table, "column": column},
        ).fetchone()
        return (row[0] if row else None)


def _ensure_users_table_schema() -> None:
    """
    Доворачиваем таблицу users до ожидаемой схемы:
      - email UNIQUE
      - full_name VARCHAR(255) NULL
      - password_hash VARCHAR(255) (переименование hashed_password → password_hash)
      - is_active BOOLEAN DEFAULT TRUE
      - индекс на email
    """
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as conn:
        # full_name
        if not _column_exists("public", "users", "full_name"):
            print("WARNING:app.main:users.full_name is missing — adding")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN full_name VARCHAR(255)"))
        # password_hash
        if _column_exists("public", "users", "hashed_password") and not _column_exists("public", "users", "password_hash"):
            print("WARNING:app.main:users.hashed_password found — renaming to password_hash")
            conn.execute(text("ALTER TABLE public.users RENAME COLUMN hashed_password TO password_hash"))
        if not _column_exists("public", "users", "password_hash"):
            conn.execute(text("ALTER TABLE public.users ADD COLUMN password_hash VARCHAR(255)"))
        # is_active
        if not _column_exists("public", "users", "is_active"):
            print("WARNING:app.main:users.is_active is missing — adding with default true")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
        # email UNIQUE + индекс
        # создаём уникальный индекс если нет
        conn.execute(text("""
            DO $$
            BEGIN
              IF NOT EXISTS (
                SELECT 1 FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relkind = 'i'
                  AND c.relname = 'ix_users_email'
                  AND n.nspname = 'public'
              ) THEN
                CREATE UNIQUE INDEX ix_users_email ON public.users (email);
              END IF;
            END$$;
        """))
    print("INFO:app.main:users table schema ensured")


def _ensure_users_role_varchar() -> None:
    """
    Приводим users.role из enum userrole в VARCHAR(20),
    чтобы ORM мог писать строки ('admin', 'promoter', 'supervisor', 'office').
    """
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as conn:
        # Узнаем текущий тип
        row = conn.execute(
            text("""
                SELECT data_type, udt_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'users'
                  AND column_name = 'role'
                LIMIT 1
            """)
        ).fetchone()
        if not row:
            return

        data_type, udt_name = row[0], row[1]
        if str(data_type).upper() == "USER-DEFINED":
            # При наличии пользовательского enum типа приводим колонку к VARCHAR,
            # предварительно удалив default (если он указывает на enum).
            try:
                conn.execute(text("ALTER TABLE public.users ALTER COLUMN role DROP DEFAULT"))
            except Exception:
                # Если default нет или уже строковый — продолжаем.
                pass

            conn.execute(text(
                """
                ALTER TABLE public.users
                ALTER COLUMN role TYPE VARCHAR(20)
                USING role::text
                """
            ))

            # Возвращаем строковый default
            conn.execute(text("ALTER TABLE public.users ALTER COLUMN role SET DEFAULT 'admin'"))

            # Пробуем удалить тип, если больше не используется
            try:
                conn.execute(text("DROP TYPE IF EXISTS userrole"))
            except Exception:
                pass

            print("INFO:app.main:users.role converted to VARCHAR(20)")


def _ensure_users_id_varchar36() -> None:
    """
    Безопасно приводим users.id к VARCHAR(36), если он ещё integer.
    Если есть FK из invites.invited_by → users.id, временно снимаем fk.
    """
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as conn:
        row = conn.execute(
            text("""
                SELECT data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'users'
                  AND column_name = 'id'
                LIMIT 1
            """)
        ).fetchone()
        if not row:
            return
        data_type = row[0]

        if str(data_type).lower() in ("integer", "bigint", "smallint"):
            print("INFO:app.main:users.id converted to VARCHAR(36)")
            # Снимем внешний ключ invites_invited_by_fkey (если есть)
            try:
                conn.execute(text("ALTER TABLE public.invites DROP CONSTRAINT IF EXISTS invites_invited_by_fkey"))
            except Exception:
                pass
            # Меняем тип id
            conn.execute(text("""
                ALTER TABLE public.users
                ALTER COLUMN id TYPE VARCHAR(36)
                USING id::varchar
            """))
            # Попытка восстановить внешний ключ, если поле есть
            try:
                # проверим наличие invited_by
                invited_by_exists = conn.execute(text("""
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = 'invites'
                      AND column_name = 'invited_by'
                """)).fetchone()
                if invited_by_exists:
                    conn.execute(text("""
                        ALTER TABLE public.invites
                        ADD CONSTRAINT invites_invited_by_fkey
                        FOREIGN KEY (invited_by) REFERENCES public.users(id)
                        ON DELETE SET NULL
                    """))
            except Exception:
                pass


# -----------------------------------------------------------------------------
# Сидирование администратора
# -----------------------------------------------------------------------------
def seed_admin(db: Session) -> None:
    """
    Создаёт администратора, если такого email ещё нет.
    role записывается строкой 'admin' (после _ensure_users_role_varchar()).
    """
    email = ADMIN_EMAIL.strip()
    if not email:
        print("WARNING:app.main:ADMIN_EMAIL is empty — skip seed_admin")
        return

    admin = db.query(User).filter(User.email == email).first()
    if admin:
        return

    pwd_hash = get_password_hash(ADMIN_PASSWORD)

    col_type = _get_column_type("public", "users", "role")
    if col_type and str(col_type).upper() == "USER-DEFINED":
        with engine.begin() as conn:
            uid = str(uuid.uuid4())
            conn.execute(
                text(
                    """
                    INSERT INTO public.users (id, email, full_name, role, password_hash, is_active)
                    VALUES (:id, :email, :full_name, CAST(:role AS userrole), :pwd, true)
                    ON CONFLICT (email) DO NOTHING
                    """
                ),
                {
                    "id": uid,
                    "email": email,
                    "full_name": "Administrator",
                    "role": "admin",
                    "pwd": pwd_hash,
                },
            )
        print(f"INFO:app.main:seed_admin inserted {email} with enum role")
        return

    admin = User(
        email=email,
        full_name="Administrator",
        role="admin",
        password_hash=pwd_hash,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f"INFO:app.main:seed_admin created {email}")


# -----------------------------------------------------------------------------
# FastAPI
# -----------------------------------------------------------------------------
app = FastAPI(title=PROJECT_NAME)

# CORS
origins = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]
if not origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роуты API v1
app.include_router(api_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
def read_root():
    return {"service": PROJECT_NAME}

# Health
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}

@app.get("/version", tags=["health"])
def version():
    return {"name": PROJECT_NAME, "env": {"ADMIN_EMAIL": ADMIN_EMAIL, "CORS_ORIGINS": CORS_ORIGINS}}


# -----------------------------------------------------------------------------
# Жизненный цикл: старт приложения
# -----------------------------------------------------------------------------
@app.on_event("startup")
def on_startup():
    # 1) создаём таблицы из моделей
    create_all()
    # 2) доворачиваем users: колонки/индексы
    _ensure_users_table_schema()
    # 3) приводим users.role (enum → VARCHAR(20))
    _ensure_users_role_varchar()
    # 4) приводим id к VARCHAR(36) — на случай старой БД; если уже в порядке — ничего не делает
    _ensure_users_id_varchar36()
    # 5) сидируем админа
    with SessionLocal() as db:
        seed_admin(db)
