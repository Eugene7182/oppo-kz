"""sku and price_list tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20240907_sku_and_pricelist"
down_revision = (
    "20240906_regions_networks_stores",
    "20250902_rename_users_to_user",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")
    op.create_table(
        "sku",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("brand", sa.String(length=100), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("attrs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_sku_brand", "sku", ["brand"], unique=False)
    op.create_index("ix_sku_model", "sku", ["model"], unique=False)
    op.create_index("ix_sku_active", "sku", ["active"], unique=False)

    op.create_table(
        "price_list",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("sku_id", sa.String(length=36), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="KZT"),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["sku_id"], ["sku.id"], ondelete="RESTRICT"),
        postgresql.ExcludeConstraint(
            ("sku_id", "="),
            (
                sa.text("daterange(valid_from, COALESCE(valid_to, 'infinity'::date), '[]')"),
                "&&",
            ),
            name="price_list_no_overlap",
            using="gist",
        ),
    )
    op.create_index(
        "ix_pricelist_sku_valid_from_desc",
        "price_list",
        ["sku_id", sa.text("valid_from DESC")],
        unique=False,
    )
    op.create_index(
        "ix_pricelist_sku_valid_to",
        "price_list",
        ["sku_id", "valid_to"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_pricelist_sku_valid_to", table_name="price_list")
    op.drop_index("ix_pricelist_sku_valid_from_desc", table_name="price_list")
    op.drop_table("price_list")
    op.drop_index("ix_sku_active", table_name="sku")
    op.drop_index("ix_sku_model", table_name="sku")
    op.drop_index("ix_sku_brand", table_name="sku")
    op.drop_table("sku")
