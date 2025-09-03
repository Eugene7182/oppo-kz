# backend/alembic/versions/0001_create_users.py
from alembic import op
import sqlalchemy as sa

revision = "0001_create_users"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="admin"),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_user_role_email", "users", ["role", "email"], unique=False)

def downgrade() -> None:
    op.drop_index("ix_user_role_email", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
