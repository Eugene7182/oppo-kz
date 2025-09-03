def _ensure_users_table_schema() -> None:
    """
    Авто-ремонт таблицы users:
    1) Если users.id = integer/bigint — находим все внешние ключи, которые ссылаются на users(id),
       снимаем их, приводим их колонки к VARCHAR(36), затем меняем тип users.id на VARCHAR(36).
       (FK можно вернуть позже, сейчас главное — поднять сервис.)
    2) Добавляем недостающие колонки: full_name, password_hash (или переименовываем hashed_password),
       is_active, role.
    3) Гарантируем уникальный индекс на email.
    """
    with engine.begin() as conn:
        # ------ читаем текущие колонки users ------
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

        # ------ если id integer/bigint — снимаем FK, меняем типы зависимых колонок и users.id ------
        id_info = cols.get("id")
        if id_info and id_info["data_type"] in ("integer", "bigint"):
            logger.warning("users.id is %s — converting to VARCHAR(36) with FK handling", id_info["data_type"])

            # 1) найдём все FK, которые ссылаются на public.users(id)
            fk_rows = conn.execute(
                text("""
                    SELECT
                        con.conname        AS constraint_name,
                        rel_t.relname      AS table_name,
                        att2.attname       AS column_name
                    FROM pg_constraint con
                    JOIN pg_class rel_t
                      ON rel_t.oid = con.conrelid
                    JOIN LATERAL unnest(con.conkey) AS fk(attnum) ON TRUE
                    JOIN pg_attribute att2
                      ON att2.attrelid = con.conrelid AND att2.attnum = fk.attnum
                    WHERE con.contype = 'f'
                      AND con.confrelid = 'public.users'::regclass
                """)
            ).mappings().all()

            # 2) снимаем эти FK
            for r in fk_rows:
                q = text(f'ALTER TABLE public."{r["table_name"]}" DROP CONSTRAINT "{r["constraint_name"]}"')
                logger.warning("Dropping FK %s on %s(%s)", r["constraint_name"], r["table_name"], r["column_name"])
                conn.execute(q)

            # 3) приводим тип зависимых колонок к VARCHAR(36)
            for r in fk_rows:
                q = text(f'ALTER TABLE public."{r["table_name"]}" ALTER COLUMN "{r["column_name"]}" TYPE VARCHAR(36) USING "{r["column_name"]}"::varchar')
                logger.warning("Altering type %s.%s -> VARCHAR(36)", r["table_name"], r["column_name"])
                conn.execute(q)

            # 4) снимаем default с users.id (если был serial/sequence) и меняем тип
            if id_info["column_default"]:
                conn.execute(text("ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT"))
            conn.execute(text("ALTER TABLE public.users ALTER COLUMN id TYPE VARCHAR(36) USING id::varchar"))
            logger.info("users.id converted to VARCHAR(36)")

        # ------ остальной ремонт колонок ------
        if "full_name" not in cols:
            logger.warning("users.full_name is missing — adding")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN full_name VARCHAR(255) NULL"))

        if "password_hash" not in cols and "hashed_password" in cols:
            logger.warning("users.hashed_password found — renaming to password_hash")
            conn.execute(text('ALTER TABLE public.users RENAME COLUMN "hashed_password" TO "password_hash"'))
            cols["password_hash"] = {"column_name": "password_hash", "data_type": "character varying", "column_default": None}

        if "password_hash" not in cols and "hashed_password" not in cols:
            logger.warning("users.password_hash is missing — adding")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT ''"))

        if "is_active" not in cols:
            logger.warning("users.is_active is missing — adding with default true")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true"))

        if "role" not in cols:
            logger.warning("users.role is missing — adding with default 'admin'")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'admin'"))

        # уникальный индекс на email
        conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_indexes
                    WHERE schemaname = 'public' AND indexname = 'ix_users_email'
                ) THEN
                    CREATE UNIQUE INDEX ix_users_email ON public.users (email);
                END IF;
            END$$;
        """))
