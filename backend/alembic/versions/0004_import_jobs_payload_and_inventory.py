import sqlalchemy as sa

from alembic import op

revision = "0004_payload_inventory"
down_revision = "0003_import_jobs"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("import_jobs", sa.Column("payload", sa.LargeBinary(), nullable=True))
    op.add_column("import_jobs", sa.Column("mime", sa.String(length=100), nullable=True))
    op.create_table(
        "stock_balances",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("store_id", sa.Integer, nullable=False),
        sa.Column("sku_id", sa.Integer, nullable=False),
        sa.Column("on_hand", sa.Float, nullable=False, server_default=sa.text("0")),
        sa.Column("in_transit", sa.Float, nullable=False, server_default=sa.text("0")),
    )
    op.create_unique_constraint("uq_balance_store_sku", "stock_balances", ["store_id", "sku_id"])


def downgrade():
    op.drop_constraint("uq_balance_store_sku", "stock_balances", type_="unique")
    op.drop_table("stock_balances")
    op.drop_column("import_jobs", "mime")
    op.drop_column("import_jobs", "payload")
