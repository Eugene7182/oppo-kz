"""add supervisor role to userrole enum

Revision ID: 2025_08_31_add_supervisor_role
Revises: <PUT_PREV_REV_ID_HERE>
Create Date: 2025-08-31
"""
from alembic import op

# IDs Alembic
revision = "2025_08_31_add_supervisor_role"
down_revision = "<PUT_PREV_REV_ID_HERE>"
branch_labels = None
depends_on = None

def upgrade():
    # Безопасно добавляем новое значение в существующий ENUM 'userrole'
    op.execute("""
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
    """)

def downgrade():
    # Откат значения из ENUM в проде обычно не делают — no-op
    pass
