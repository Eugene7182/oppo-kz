from __future__ import annotations

"""Create users table and roles enum."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20240905_create_users_and_roles"
down_revision = "2025_09_01_store_coefficients"
branch_labels = None
depends_on = None

ROLE_ENUM = sa.Enum("admin", "office", "supervisor", "promoter", name="userrole", native_enum=True)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        ROLE_ENUM.create(bind, checkfirst=True)
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("role", ROLE_ENUM, nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_users_role", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        ROLE_ENUM.drop(bind, checkfirst=True)
