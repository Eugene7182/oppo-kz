# -*- coding: utf-8 -*-
"""app_settings + push_subscriptions"""

from alembic import op
import sqlalchemy as sa

revision = "20250901_webpush_and_settings"
down_revision = "2025_09_01_auth_invites"  # <-- ОБНОВЛЕНО
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(length=100), primary_key=True),
        sa.Column("value", sa.Text(), nullable=False),
    )
    op.create_table(
        "push_subscriptions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("endpoint", sa.String(length=1000), nullable=False),
        sa.Column("p256dh", sa.String(length=255), nullable=False),
        sa.Column("auth", sa.String(length=255), nullable=False),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("last_sent_at", sa.DateTime(), nullable=True),
    )
    op.create_unique_constraint("uq_push_endpoint", "push_subscriptions", ["endpoint"])

def downgrade() -> None:
    op.drop_constraint("uq_push_endpoint", "push_subscriptions", type_="unique")
    op.drop_table("push_subscriptions")
    op.drop_table("app_settings")
