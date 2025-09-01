# -*- coding: utf-8 -*-
"""add supervisor role to userrole enum"""

from alembic import op

# Alembic IDs
revision = "2025_08_31_add_supervisor_role"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Безопасно добавляем значение 'supervisor' в существующий ENUM userrole
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                WHERE t.typname = 'userrole' AND e.enumlabel = 'supervisor'
            ) THEN
                ALTER TYPE userrole ADD VALUE 'supervisor';
            END IF;
        END$$;
        """
    )


def downgrade() -> None:
    # Удалять значения из ENUM в проде обычно не делают; оставляем no-op
    pass
