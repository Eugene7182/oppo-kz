"""create sales tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20250915_create_sales_tables"
down_revision = "20240907_sku_and_pricelist"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sales_promoters",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("store_id", sa.String(length=36), nullable=False),
        sa.Column("sku_id", sa.String(length=36), nullable=False),
        sa.Column("promoter_id", sa.String(length=36), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("sold_at", sa.Date(), nullable=False),
        sa.Column("approved_by_office", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["sku_id"], ["sku.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["promoter_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.CheckConstraint("qty > 0", name="ck_sales_promoters_qty_positive"),
        sa.CheckConstraint("amount >= 0", name="ck_sales_promoters_amount_non_negative"),
    )
    op.create_index(
        "ix_sales_promoters_store_id_sold_at",
        "sales_promoters",
        ["store_id", "sold_at"],
        unique=False,
    )
    op.create_index(
        "ix_sales_promoters_sku_id_sold_at",
        "sales_promoters",
        ["sku_id", "sold_at"],
        unique=False,
    )
    op.create_index(
        "ix_sales_promoters_promoter_id_sold_at",
        "sales_promoters",
        ["promoter_id", "sold_at"],
        unique=False,
    )
    op.create_index(
        "ix_sales_promoters_approved",
        "sales_promoters",
        ["approved_by_office"],
        unique=False,
    )

    op.create_table(
        "sales_retail",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("store_id", sa.String(length=36), nullable=False),
        sa.Column("sku_id", sa.String(length=36), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("sold_at", sa.Date(), nullable=False),
        sa.Column("feed_batch_id", sa.String(), nullable=True),
        sa.Column("external_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["sku_id"], ["sku.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("qty > 0", name="ck_sales_retail_qty_positive"),
        sa.CheckConstraint("amount >= 0", name="ck_sales_retail_amount_non_negative"),
    )
    op.create_index(
        "ix_sales_retail_store_id_sold_at",
        "sales_retail",
        ["store_id", "sold_at"],
        unique=False,
    )
    op.create_index(
        "ix_sales_retail_sku_id_sold_at",
        "sales_retail",
        ["sku_id", "sold_at"],
        unique=False,
    )
    op.create_index(
        "ix_sales_retail_feed_batch_id",
        "sales_retail",
        ["feed_batch_id"],
        unique=False,
    )
    op.create_index(
        "ux_sales_retail_external_id",
        "sales_retail",
        ["external_id"],
        unique=True,
        postgresql_where=sa.text("external_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("ux_sales_retail_external_id", table_name="sales_retail")
    op.drop_index("ix_sales_retail_feed_batch_id", table_name="sales_retail")
    op.drop_index("ix_sales_retail_sku_id_sold_at", table_name="sales_retail")
    op.drop_index("ix_sales_retail_store_id_sold_at", table_name="sales_retail")
    op.drop_table("sales_retail")
    op.drop_index("ix_sales_promoters_approved", table_name="sales_promoters")
    op.drop_index("ix_sales_promoters_promoter_id_sold_at", table_name="sales_promoters")
    op.drop_index("ix_sales_promoters_sku_id_sold_at", table_name="sales_promoters")
    op.drop_index("ix_sales_promoters_store_id_sold_at", table_name="sales_promoters")
    op.drop_table("sales_promoters")
