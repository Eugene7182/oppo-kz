def _ensure_users_table_schema() -> None:
    """
    Авто-ремонт таблицы users:
    - добавляет недостающие колонки (full_name, password_hash, is_active, role),
    - переименовывает hashed_password -> password_hash,
    - КЛЮЧЕВОЕ: конвертирует id из integer/bigint в VARCHAR(36), если нужно.
    - гарантирует уникальный индекс на email.
    """
    from sqlalchemy import text

    with engine.begin() as conn:
        rows = conn.execute(
            text("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'users'
            """)
        ).mappings().all()

        cols = {r["column_name"]: r for r in rows}
        if not cols:
            logger.info("users table not found in public schema (will be created by create_all)")
            return

        # --- 0) id: integer -> varchar(36)
        id_info = cols.get("id")
        if id_info and id_info["data_type"] in ("integer", "bigint"):
            logger.warning("users.id is %s — converting to VARCHAR(36)", id_info["data_type"])
            # Если serial, снимем default nextval(...)
            if id_info["column_default"]:
                conn.execute(text("ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT"))
            # Конвертируем тип с сохранением PK
            conn.execute(text("ALTER TABLE public.users ALTER COLUMN id TYPE VARCHAR(36) USING id::varchar"))
            # Обновим локальный слепок
            id_info["data_type"] = "character varying"

        # --- 1) full_name
        if "full_name" not in cols:
            logger.warning("users.full_name is missing — adding")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN full_name VARCHAR(255) NULL"))

        # --- 2) password_hash
        if "password_hash" not in cols and "hashed_password" in cols:
            logger.warning("users.hashed_password found — renaming to password_hash")
            conn.execute(text('ALTER TABLE public.users RENAME COLUMN "hashed_password" TO "password_hash"'))
            cols["password_hash"] = {"column_name": "password_hash", "data_type": "character varying", "column_default": None}

        if "password_hash" not in cols and "hashed_password" not in cols:
            logger.warning("users.password_hash is missing — adding")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT ''"))

        # --- 3) is_active
        if "is_active" not in cols:
            logger.warning("users.is_active is missing — adding with default true")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true"))

        # --- 4) role
        if "role" not in cols:
            logger.warning("users.role is missing — adding with default 'admin'")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'admin'"))

        # --- 5) уникальный индекс на email
        conn.execute(
            text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes
                        WHERE schemaname = 'public' AND indexname = 'ix_users_email'
                    ) THEN
                        CREATE UNIQUE INDEX ix_users_email ON public.users (email);
                    END IF;
                END$$;
            """)
        )
