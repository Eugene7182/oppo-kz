# -*- coding: utf-8 -*-
"""bootstrap userrole enum and add supervisor value safely"""

import sqlalchemy as sa  # noqa: F401

from alembic import op

# Самая первая миграция
revision = "2025_08_31_add_supervisor_role"
down_revision = "0004_payload_inventory"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаём ENUM userrole, если его ещё нет.
    # Если тип уже есть, но нет значения 'supervisor' — добавляем.
    op.execute(
        """
        DO $$
        BEGIN
            -- 1) Если ENUM userrole не существует — создаём сразу со всеми базовыми ролями
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
                CREATE TYPE userrole AS ENUM ('admin','office','promoter','supervisor');
            ELSE
                -- 2) Если тип есть, но без 'supervisor' — добавим безопасно
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
    # Откат значений из ENUM в проде делать опасно: оставляем no-op
    pass
