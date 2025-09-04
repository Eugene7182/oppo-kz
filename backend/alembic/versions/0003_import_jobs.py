
from alembic import op
import sqlalchemy as sa

revision = "0003_import_jobs"
down_revision = "0002_indexes"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "import_jobs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="queued"),
        sa.Column("progress", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total", sa.Integer, nullable=False, server_default="0"),
        sa.Column("processed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_import_jobs_status", "import_jobs", ["status"])

def downgrade():
    op.drop_index("ix_import_jobs_status", table_name="import_jobs")
    op.drop_table("import_jobs")
