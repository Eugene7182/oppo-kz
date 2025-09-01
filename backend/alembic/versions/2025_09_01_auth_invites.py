# -*- coding: utf-8 -*-
"""invites for registration + auth helpers"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM as PGEnum

# Уникальные идентификаторы ревизий
revision = "2025_09_01_auth_invites"
down_revision = "2025_09_01_features_audit_bonus_campaigns"
branch_labels = None
depends_on = None

# ВАЖНО: переиспользуем существующий тип ENUM 'userrole'
# create_type=False — не пытаться создавать тип заново
USERROLE = PGEnum(name="userrole", create_type=False)


def upgrade() -> None:
    op.create_table(
        "invites",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("role", USERROLE, nullable=False),  # используем существующий ENUM
        sa.Column("token", sa.String(length=64), nullable=False, unique=True),
        sa.Column(
            "invited_by",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("note", sa.String(length=300), nullable=True),
    )
    op.create_index("ix_invites_email", "invites", ["email"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_invites_email", table_name="invites")
    op.drop_table("invites")
