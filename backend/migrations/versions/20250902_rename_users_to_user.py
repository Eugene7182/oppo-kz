import sqlalchemy as sa  # noqa: F401

from alembic import op

revision = "20250902_rename_users_to_user"
down_revision = "20250901_all_changes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("users", "user")
    op.execute("ALTER INDEX IF EXISTS ix_users_email RENAME TO ix_user_email")


def downgrade() -> None:
    op.rename_table("user", "users")
    op.execute("ALTER INDEX IF EXISTS ix_user_email RENAME TO ix_users_email")
