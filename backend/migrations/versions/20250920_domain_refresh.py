"""Domain refresh for OPPO KZ core tables."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20250920_domain_refresh"
down_revision = "20250915_create_sales_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- users extra columns ---
    op.add_column("users", sa.Column("region_id", sa.String(length=36), nullable=True))
    op.add_column(
        "users",
        sa.Column(
            "status",
            sa.Enum("active", "inactive", "invited", name="userstatus"),
            nullable=False,
            server_default="active",
        ),
    )
    op.add_column("users", sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key(
        "fk_users_region_id_regions",
        "users",
        "regions",
        ["region_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # --- invites rebuild ---
    op.execute("DROP TABLE IF EXISTS invites")
    op.create_table(
        "invites",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role_requested", sa.String(length=20), nullable=False),
        sa.Column(
            "scope_type",
            sa.Enum("country", "region", "store", name="invitescopetype"),
            nullable=True,
        ),
        sa.Column("scope_id", sa.String(length=36), nullable=True),
        sa.Column("token", sa.String(length=64), nullable=False, unique=True),
        sa.Column("invited_by", sa.String(length=36), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "accepted", "revoked", "expired", name="invitestatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["invited_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("email", "status", name="uq_invites_email_pending"),
        sa.Index("ix_invites_token", "token", unique=True),
        sa.Index("ix_invites_status", "status"),
    )

    # --- reference tables ---
    op.create_table(
        "cities",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("region_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["region_id"], ["regions.id"], ondelete="RESTRICT"),
        sa.Index("ix_cities_region_id", "region_id"),
        sa.UniqueConstraint("region_id", "name", name="uq_cities_region_name"),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("sku", sa.String(length=64), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column(
            "status",
            sa.Enum("active", "eol", "archived", name="productstatus"),
            nullable=False,
            server_default="active",
        ),
        sa.Column("attrs_json", sa.JSON().with_variant(postgresql.JSONB, "postgresql"), nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Index("ix_products_sku", "sku", unique=True),
    )

    # --- sales ---
    op.create_table(
        "sales",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("promoter_id", sa.String(length=36), nullable=False),
        sa.Column("store_id", sa.String(length=36), nullable=False),
        sa.Column("sku_id", sa.String(length=36), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column(
            "status",
            sa.Enum("active", "deleted", name="salestatus"),
            nullable=False,
            server_default="active",
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["promoter_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["sku_id"], ["products.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("qty >= 0", name="ck_sales_qty_non_negative"),
        sa.CheckConstraint("price >= 0", name="ck_sales_price_non_negative"),
        sa.UniqueConstraint("id", name="uq_sales_id"),
        sa.Index("ix_sales_promoter_date", "promoter_id", "date"),
        sa.Index("ix_sales_store_date", "store_id", "date"),
    )

    op.create_table(
        "sale_revisions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("sale_id", sa.String(length=36), nullable=False),
        sa.Column("changed_by", sa.String(length=36), nullable=True),
        sa.Column(
            "before_json",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=True,
        ),
        sa.Column(
            "after_json",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=True,
        ),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"], ondelete="SET NULL"),
        sa.Index("ix_sale_revisions_sale_id", "sale_id"),
    )

    op.create_table(
        "sale_corrections",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("sale_id", sa.String(length=36), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("delta_qty", sa.Integer(), nullable=False),
        sa.Column("delta_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.Index("ix_sale_corrections_sale_id", "sale_id"),
    )

    # --- plans ---
    op.create_table(
        "plan_promoter_month",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("period_ym", sa.String(length=7), nullable=False),
        sa.Column("promoter_id", sa.String(length=36), nullable=False),
        sa.Column("store_id", sa.String(length=36), nullable=True),
        sa.Column("target_units", sa.Integer(), nullable=True),
        sa.Column("target_revenue", sa.Numeric(14, 2), nullable=True),
        sa.Column(
            "source",
            sa.Enum("manual", "import", "system", name="plansource"),
            nullable=False,
            server_default="manual",
        ),
        sa.Column("updated_by", sa.String(length=36), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["promoter_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.Index("ix_plan_promoter_period", "promoter_id", "period_ym"),
    )

    op.create_table(
        "plan_audit",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("plan_id", sa.String(length=36), nullable=False),
        sa.Column(
            "before_json",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=True,
        ),
        sa.Column(
            "after_json",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=True,
        ),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("updated_by", sa.String(length=36), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["plan_id"], ["plan_promoter_month.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.Index("ix_plan_audit_plan_id", "plan_id"),
    )

    # --- bonuses ---
    op.create_table(
        "bonus_schemes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("network_id", sa.String(length=36), nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("draft", "published", name="bonusschemestatus"),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["network_id"], ["networks.id"], ondelete="CASCADE"),
        sa.Index("ix_bonus_schemes_network", "network_id"),
    )

    op.create_table(
        "bonus_rules",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("scheme_id", sa.String(length=36), nullable=False),
        sa.Column(
            "selector_type",
            sa.Enum("sku", "series", "all", name="bonusselectortype"),
            nullable=False,
        ),
        sa.Column("selector_value", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "conditions_json",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["scheme_id"], ["bonus_schemes.id"], ondelete="CASCADE"),
        sa.Index("ix_bonus_rules_scheme", "scheme_id"),
    )

    # --- closed periods ---
    op.create_table(
        "closed_periods",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "scope",
            sa.Enum("country", "region", "store", name="closedscope"),
            nullable=False,
        ),
        sa.Column("scope_id", sa.String(length=36), nullable=True),
        sa.Column("from_date", sa.Date(), nullable=False),
        sa.Column("to_date", sa.Date(), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.Index("ix_closed_period_scope", "scope", "scope_id"),
    )

    # --- audit log ---
    op.create_table(
        "audit_log",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("ts", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actor_id", sa.String(length=36), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=True),
        sa.Column(
            "before_json",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=True,
        ),
        sa.Column(
            "after_json",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("closed_periods")
    op.drop_table("bonus_rules")
    op.drop_table("bonus_schemes")
    op.drop_table("plan_audit")
    op.drop_table("plan_promoter_month")
    op.drop_table("sale_corrections")
    op.drop_table("sale_revisions")
    op.drop_table("sales")
    op.drop_table("products")
    op.drop_table("cities")
    op.drop_table("invites")
    op.drop_constraint("fk_users_region_id_regions", "users", type_="foreignkey")
    op.drop_column("users", "locked_at")
    op.drop_column("users", "status")
    op.drop_column("users", "region_id")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS userstatus")
        op.execute("DROP TYPE IF EXISTS invitestatus")
        op.execute("DROP TYPE IF EXISTS invitescopetype")
        op.execute("DROP TYPE IF EXISTS productstatus")
        op.execute("DROP TYPE IF EXISTS salestatus")
        op.execute("DROP TYPE IF EXISTS plansource")
        op.execute("DROP TYPE IF EXISTS bonusschemestatus")
        op.execute("DROP TYPE IF EXISTS bonusselectortype")
        op.execute("DROP TYPE IF EXISTS closedscope")
