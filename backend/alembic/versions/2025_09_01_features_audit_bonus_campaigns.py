from alembic import op
import sqlalchemy as sa

revision = '2025_09_01_features_audit_bonus_campaigns'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('actor_username', sa.String(length=120), nullable=True, index=True),
        sa.Column('action', sa.String(length=64), nullable=False, index=True),
        sa.Column('entity', sa.String(length=64), nullable=True, index=True),
        sa.Column('entity_id', sa.String(length=64), nullable=True, index=True),
        sa.Column('before_json', sa.Text(), nullable=True),
        sa.Column('after_json', sa.Text(), nullable=True),
        sa.Column('ts', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_audit_ts', 'audit_logs', ['ts'], unique=False)

    op.create_table('bonus_payouts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('period_from', sa.Date(), nullable=False),
        sa.Column('period_to', sa.Date(), nullable=False),
        sa.Column('promoter_username', sa.String(length=120), nullable=False),
        sa.Column('amount', sa.Numeric(12,2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_bonus_period', 'bonus_payouts', ['period_from','period_to'], unique=False)

    op.create_table('campaigns',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(length=120), nullable=False, unique=True),
        sa.Column('start', sa.Date(), nullable=False),
        sa.Column('end', sa.Date(), nullable=False),
        sa.Column('note', sa.String(length=300), nullable=True),
        sa.Column('stores_json', sa.Text(), nullable=True),
        sa.Column('skus_json', sa.Text(), nullable=True),
        sa.Column('mechanics_json', sa.Text(), nullable=True),
    )

def downgrade() -> None:
    op.drop_table('campaigns')
    op.drop_index('ix_bonus_period', table_name='bonus_payouts')
    op.drop_table('bonus_payouts')
    op.drop_index('ix_audit_ts', table_name='audit_logs')
    op.drop_table('audit_logs')
