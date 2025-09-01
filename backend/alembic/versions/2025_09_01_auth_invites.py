# -*- coding: utf-8 -*-
"""invites for registration + auth helpers"""

from alembic import op
import sqlalchemy as sa

# эта ревизия идёт ПОСЛЕ features_audit_bonus_campaigns
revision = "2025_09_01_auth_invites"
down_revision = "2025_09_01_features_audit_bonus_campaigns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Таблица инвайтов. Роль — из ENUM userrole (мы ранее добавили supervisor).
    op.create_table(
        "invites",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("role", sa.Enum(name="userrole", create_type=False), nullable=False),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("used_by", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("note", sa.String(length=300), nullable=True),
    )
    op.create_index("ix_invites_code", "invites", ["code"], unique=True)
    op.create_index("ix_invites_email", "invites", ["email"], unique=False)
    op.create_index("ix_invites_created_by", "invites", ["created_by"], unique=False)
    op.create_index("ix_invites_used_by", "invites", ["used_by"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_invites_used_by", table_name="invites")
    op.drop_index("ix_invites_created_by", table_name="invites")
    op.drop_index("ix_invites_email", table_name="invites")
    op.drop_index("ix_invites_code", table_name="invites")
    op.drop_table("invites")
