# -*- coding: utf-8 -*-
"""widen alembic_version.version_num to 255"""

import sqlalchemy as sa  # noqa: F401

from alembic import op

# Короткий revision, чтобы поместился в старые 32 символа
revision = "2025_09_01_alembic_verlen"
down_revision = "2025_09_01_store_coefficients"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    У некоторых БД Alembic создаёт alembic_version.version_num как VARCHAR(32).
    Дальше у нас ревизии длиннее 32, поэтому расширяем до 255.
    """
    op.execute(
        """
        DO $$
        BEGIN
            -- Если таблица есть и длина поля < 255 — расширяем
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'alembic_version'
                  AND column_name = 'version_num'
                  AND (character_maximum_length IS NOT NULL AND character_maximum_length < 255)
            ) THEN
                ALTER TABLE alembic_version
                ALTER COLUMN version_num TYPE VARCHAR(255);
            END IF;
        EXCEPTION
            WHEN undefined_table THEN
                -- На всякий случай: если alembic_version ещё не создана (маловероятно посреди цепочки)
                NULL;
        END
        $$;
        """
    )


def downgrade() -> None:
    # Сжимать обратно не требуется и небезопасно (может обрезать текущий version_num).
    pass
