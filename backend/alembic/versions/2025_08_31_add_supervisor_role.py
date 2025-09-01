# -*- coding: utf-8 -*-
"""bootstrap userrole enum and add supervisor value"""

from alembic import op

# Эта миграция должна быть самой первой
revision = "2025_08_31_add_supervisor_role"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаём ENUM userrole, если его ещё нет.
    # Если уже есть, но без значения 'supervisor' — добавляем безопасно.
    op.execute(
        """
        DO $$
        BEGIN
            -- 1) Если ENUM userrole ещё не создан, создаём сразу с полным набором ролей
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
                CREATE TYPE userrole AS ENUM ('admin','office','promoter','supervisor');
            ELSE
                -- 2) Если тип уже есть, но значения 'supervisor' нет — добавим
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_type t
                    JOIN pg_enum e ON t.oid = e.enumtypid
                    WHERE t.typname = 'userrole' AND e.enumlabel = 'supervisor'
                ) THEN
                    ALTER TYPE userrole ADD VALUE 'supervisor';
                END IF;
            END IF;
        END$$;
        """
    )


def downgrade() -> None:
    --  В проде удалять значения из ENUM опасно и сложно, оставляем no-op
    pass
