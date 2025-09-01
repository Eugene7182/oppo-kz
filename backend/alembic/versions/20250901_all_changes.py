# -*- coding: utf-8 -*-
"""All changes consolidated"""

from alembic import op
import sqlalchemy as sa

# УНИКАЛЬНЫЕ ИДЫ РЕВИЗИЙ
revision = "20250901_all_changes"
# ВАЖНО: подставь сюда ИД предыдущей миграции ИЗ ЕЁ ПЕРЕМЕННОЙ `revision`
# например, из файла 2025_08_31_add_supervisor_role.py
down_revision = "2025_08_31_add_supervisor_role"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users: добавляем поля, если их ещё нет
    op.execute("""
        ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);
        ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name  VARCHAR(100);
        ALTER TABLE users ADD COLUMN IF NOT EXISTS position   VARCHAR(150);
    """)

    # notifications
    op.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(200) NOT NULL,
            body TEXT NULL,
            kind VARCHAR(50) NOT NULL DEFAULT 'info',
            for_date DATE NULL,
            is_read BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP NOT NULL DEFAULT now()
        );
    """)

    # notification_prefs (1:1 к users)
    op.execute("""
        CREATE TABLE IF NOT EXISTS notification_prefs (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            enable_time_reminders BOOLEAN NOT NULL DEFAULT FALSE,
            times TIME[] NULL,
            saturday_cutoff_hour INTEGER NOT NULL DEFAULT 16,
            enabled BOOLEAN NOT NULL DEFAULT TRUE
        );
    """)

    # бонусы за перевыполнение
    op.execute("""
        CREATE TABLE IF NOT EXISTS bonus_overachievement_rules (
            id SERIAL PRIMARY KEY,
            bonus_grid_id INTEGER NOT NULL REFERENCES bonus_grids(id) ON DELETE CASCADE,
            threshold_percent INTEGER NOT NULL,
            bonus_amount NUMERIC(12,2) NOT NULL DEFAULT 0
        );
    """)

    # заявки на сток (enum + таблица)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'stock_request_status') THEN
                CREATE TYPE stock_request_status AS ENUM ('new','approved','rejected','fulfilled');
            END IF;
        END $$;
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS stock_requests (
            id SERIAL PRIMARY KEY,
            promoter_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
            supervisor_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
            store_id INTEGER NULL REFERENCES stores(id) ON DELETE SET NULL,
            sku_id INTEGER NULL REFERENCES skus(id) ON DELETE SET NULL,
            memory_option VARCHAR(50) NULL,
            qty INTEGER NOT NULL DEFAULT 1,
            comment TEXT NULL,
            status stock_request_status NOT NULL DEFAULT 'new',
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        );
    """)

    # app_settings (k/v)
    op.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            key VARCHAR(100) PRIMARY KEY,
            value TEXT NOT NULL
        );
    """)

    # web push subscriptions
    op.execute("""
        CREATE TABLE IF NOT EXISTS push_subscriptions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            endpoint VARCHAR(1000) NOT NULL,
            p256dh VARCHAR(255) NOT NULL,
            auth VARCHAR(255) NOT NULL,
            user_agent VARCHAR(255) NULL,
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            last_sent_at TIMESTAMP NULL
        );
    """)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_push_endpoint ON push_subscriptions(endpoint);
    """)


def downgrade() -> None:
    # порядок отката обратный зависимостям
    op.execute("DROP INDEX IF EXISTS uq_push_endpoint;")
    op.execute("DROP TABLE IF EXISTS push_subscriptions;")
    op.execute("DROP TABLE IF EXISTS app_settings;")
    op.execute("DROP TABLE IF EXISTS stock_requests;")
    op.execute("DROP TABLE IF EXISTS bonus_overachievement_rules;")
    op.execute("DROP TABLE IF EXISTS notification_prefs;")
    op.execute("DROP TABLE IF EXISTS notifications;")

    op.execute("""
        ALTER TABLE users DROP COLUMN IF EXISTS position;
        ALTER TABLE users DROP COLUMN IF EXISTS last_name;
        ALTER TABLE users DROP COLUMN IF EXISTS first_name;
    """)

    # enum удаляем только если больше нигде не используется
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'stock_request_status') THEN
                DROP TYPE stock_request_status;
            END IF;
        END $$;
    """)
