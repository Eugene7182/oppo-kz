def _ensure_users_table_schema() -> None:
    """
    Авто-ремонт схемы без потери данных:
    - снимаем FK на users(id), приводим зависимые колонки к VARCHAR(36), конвертируем users.id -> VARCHAR(36)
    - добавляем недостающие поля (full_name, password_hash, is_active, role)
    - если role имеет enum-тип (userrole и т.п.), конвертируем в VARCHAR(20)
    - аналогично правим invites.role, если там enum
    - гарантируем уникальный индекс на users.email
    """
    with engine.begin() as conn:
        # ---------- users: список колонок ----------
        rows = conn.execute(text("""
            SELECT column_name, data_type, udt_name, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'users'
        """)).mappings().all()
        cols = {r["column_name"]: r for r in rows}

        if not cols:
            logger.info("users table not found in public schema (will be created by create_all)")
            return

        # ---------- users.id: integer -> varchar(36) с учётом FK ----------
        id_info = cols.get("id")
        if id_info and id_info["data_type"] in ("integer", "bigint"):
            logger.warning("users.id is %s — converting to VARCHAR(36) with FK handling", id_info["data_type"])
            fk_rows = conn.execute(text("""
                SELECT con.conname AS constraint_name, rel_t.relname AS table_name, att2.attname AS column_name
                FROM pg_constraint con
                JOIN pg_class rel_t ON rel_t.oid = con.conrelid
                JOIN LATERAL unnest(con.conkey) AS fk(attnum) ON TRUE
                JOIN pg_attribute att2 ON att2.attrelid = con.conrelid AND att2.attnum = fk.attnum
                WHERE con.contype='f' AND con.confrelid='public.users'::regclass
            """)).mappings().all()

            for r in fk_rows:
                logger.warning('Dropping FK %s on %s(%s)', r["constraint_name"], r["table_name"], r["column_name"])
                conn.execute(text(f'ALTER TABLE public."{r["table_name"]}" DROP CONSTRAINT "{r["constraint_name"]}"'))

            for r in fk_rows:
                logger.warning('Altering type %s.%s -> VARCHAR(36)', r["table_name"], r["column_name"])
                conn.execute(text(f'ALTER TABLE public."{r["table_name"]}" ALTER COLUMN "{r["column_name"]}" TYPE VARCHAR(36) USING "{r["column_name"]}"::varchar'))

            if id_info["column_default"]:
                conn.execute(text("ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT"))
            conn.execute(text("ALTER TABLE public.users ALTER COLUMN id TYPE VARCHAR(36) USING id::varchar"))
            logger.info("users.id converted to VARCHAR(36)")

        # ---------- users.role: если enum (USER-DEFINED), переводим в VARCHAR(20) ----------
        role_info = cols.get("role")
        if role_info and role_info["data_type"] == "USER-DEFINED":
            logger.warning("users.role is enum (%s) — converting to VARCHAR(20)", role_info.get("udt_name"))
            conn.execute(text("ALTER TABLE public.users ALTER COLUMN role TYPE VARCHAR(20) USING role::text"))

        # ---------- добавляем недостающие колонки ----------
        if "full_name" not in cols:
            logger.warning("users.full_name is missing — adding")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN full_name VARCHAR(255) NULL"))

        if "password_hash" not in cols and "hashed_password" in cols:
            logger.warning("users.hashed_password found — renaming to password_hash")
            conn.execute(text('ALTER TABLE public.users RENAME COLUMN "hashed_password" TO "password_hash"'))
            cols["password_hash"] = {"column_name": "password_hash", "data_type": "character varying", "udt_name": "varchar", "column_default": None}

        if "password_hash" not in cols and "hashed_password" not in cols:
            logger.warning("users.password_hash is missing — adding")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT ''"))

        if "is_active" not in cols:
            logger.warning("users.is_active is missing — adding with default true")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true"))

        if "role" not in cols:
            logger.warning("users.role is missing — adding with default 'admin'")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'admin'"))

        # ---------- invites.role: если enum — тоже конвертируем ----------
        inv_cols = conn.execute(text("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'invites'
        """)).mappings().all()
        if inv_cols:
            inv_cols_map = {r["column_name"]: r for r in inv_cols}
            inv_role = inv_cols_map.get("role")
            if inv_role and inv_role["data_type"] == "USER-DEFINED":
                logger.warning("invites.role is enum (%s) — converting to VARCHAR(20)", inv_role.get("udt_name"))
                conn.execute(text("ALTER TABLE public.invites ALTER COLUMN role TYPE VARCHAR(20) USING role::text"))

        # ---------- уникальный индекс на email ----------
        conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_indexes
                    WHERE schemaname='public' AND indexname='ix_users_email'
                ) THEN
                    CREATE UNIQUE INDEX ix_users_email ON public.users (email);
                END IF;
            END$$;
        """))
