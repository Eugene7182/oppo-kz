# backend/app/db/session.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Читаем DSN. Фоллбек на Render-ные переменные тоже поддержим
DB_DSN = (
    os.getenv("DB_DSN")
    or os.getenv("DATABASE_URL")            # на всякий случай
    or "sqlite:///./data.db"                # локальный фоллбек
)

# Нормализация префикса, если вдруг придёт "postgres://"
if DB_DSN.startswith("postgres://"):
    DB_DSN = DB_DSN.replace("postgres://", "postgresql+psycopg://", 1)
# Если Render дал "postgresql://", явно укажем драйвер psycopg3
if DB_DSN.startswith("postgresql://"):
    DB_DSN = DB_DSN.replace("postgresql://", "postgresql+psycopg://", 1)

connect_args = {"check_same_thread": False} if DB_DSN.startswith("sqlite") else {}

engine = create_engine(
    DB_DSN,
    pool_pre_ping=True,
    connect_args=connect_args,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
