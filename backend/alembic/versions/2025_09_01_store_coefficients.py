# -*- coding: utf-8 -*-
"""store coefficients table"""

from alembic import op
import sqlalchemy as sa

revision = "2025_09_01_store_coefficients"
down_revision = "2025_08_31_add_supervisor_role"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "store_coefficients",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "store_id",
            sa.Integer,
            sa.ForeignKey("stores.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("value", sa.Numeric(6, 2), nullable=True),
        sa.Column("note", sa.String(length=200), nullable=True),
        sa.Column("valid_from", sa.Date, nullable=False),
        sa.Column("valid_to", sa.Date, nullable=True),
    )
    op.create_unique_constraint(
        "uq_store_coeff_key",
        "store_coefficients",
        ["store_id", "code", "valid_from"],
    )
    op.create_index(
        "ix_store_coeff_active",
        "store_coefficients",
        ["store_id", "code", "valid_from", "valid_to"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_store_coeff_active", table_name="store_coefficients")
    op.drop_constraint("uq_store_coeff_key", "store_coefficients", type_="unique")
    op.drop_table("store_coefficients")
