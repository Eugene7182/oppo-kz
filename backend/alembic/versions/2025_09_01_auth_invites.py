from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# ревизию назови как тебе удобно, главное — уникально
revision = "2025_09_01_auth_invites"
down_revision = None  # если у тебя уже есть ревизии — подставь последнюю, например "2025_08_31_add_supervisor_role"
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    insp = Inspector.from_engine(bind)

    # создаём таблицу invite, если её нет
    if "invite" not in insp.get_table_names():
        op.create_table(
            "invite",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("code", sa.String(length=64), nullable=False),
            sa.Column("username", sa.String(length=128), nullable=False),
            sa.Column("full_name", sa.String(length=256), nullable=True),
            sa.Column("role", sa.String(length=32), nullable=False),
            sa.Column("email", sa.String(length=256), nullable=True),
            sa.Column("is_used", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("created_by", sa.String(length=36), sa.ForeignKey("user.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_invite_code", "invite", ["code"], unique=True)

def downgrade() -> None:
    op.drop_index("ix_invite_code", table_name="invite")
    op.drop_table("invite")
