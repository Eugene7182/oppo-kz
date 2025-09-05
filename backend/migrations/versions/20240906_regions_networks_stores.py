"""regions, networks, stores tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20240906_regions_networks_stores"
down_revision = "20240905_create_users_and_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "regions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
    )
    op.create_index("ix_regions_name", "regions", ["name"], unique=False)

    op.create_table(
        "networks",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
    )
    op.create_index("ix_networks_name", "networks", ["name"], unique=False)

    op.create_table(
        "stores",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("network_id", sa.String(length=36), nullable=False),
        sa.Column("region_id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["network_id"], ["networks.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["region_id"], ["regions.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("network_id", "code", name="uq_stores_network_code"),
    )
    op.create_index("ix_stores_network_id", "stores", ["network_id"], unique=False)
    op.create_index("ix_stores_region_id", "stores", ["region_id"], unique=False)
    op.create_index("ix_stores_active", "stores", ["active"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_stores_active", table_name="stores")
    op.drop_index("ix_stores_region_id", table_name="stores")
    op.drop_index("ix_stores_network_id", table_name="stores")
    op.drop_table("stores")
    op.drop_index("ix_networks_name", table_name="networks")
    op.drop_table("networks")
    op.drop_index("ix_regions_name", table_name="regions")
    op.drop_table("regions")
