# -*- coding: utf-8 -*-
"""store coefficients table

Создаёт таблицу коэффициентов по магазинам.
Зависит от bootstrap-миграции, где создаются базовые справочники (stores).
"""

from alembic import op
import sqlalchemy as sa

# ИД ревизии и порядок
revision = "2025_09_01_store_coefficients"
down_revision = "2025_08_31_01_bootstrap_core"  # важно: идём после bootstrap_core
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Создаём таблицу:
      - store_id: FK -> stores.id (CASCADE при удалении магазина)
      - code: произвольный код коэффициента (например, "ABC", "K1", тип/категория и т.п.)
      - value: значение коэффициента (число с точностью до сотых, формат NUMERIC(6,2))
      - note: комментарий
      - valid_from/valid_to: период действия
    Дополнительно индексы для частых выборок.
    """
    op.create_table(
        "store_coefficients",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "store_id",
            sa.Integer,
            sa.ForeignKey("stores.id", ondelete="CASCADE"),
            nullable=False,
            comment="FK на stores.id",
        ),
        sa.Column("code", sa.String(length=16), nullable=False, comment="Код коэффициента"),
        sa.Column("value", sa.Numeric(6, 2), nullable=True, comment="Значение коэффициента"),
        sa.Column("note", sa.String(length=200), nullable=True, comment="Комментарий"),
        sa.Column("valid_from", sa.Date, nullable=False, comment="Дата начала действия"),
        sa.Column("valid_to", sa.Date, nullable=True, comment="Дата окончания действия"),
        # Если нужно запретить дубликаты на одинаковый период/код — раскомментируй и адаптируй:
        # sa.UniqueConstraint("store_id", "code", "valid_from", name="uq_store_coefficients_store_code_from"),
    )

    # Полезные индексы: по магазину, по периоду, по коду
    op.create_index(
        "ix_store_coefficients_store_id",
        "store_coefficients",
        ["store_id"],
        unique=False,
    )
    op.create_index(
        "ix_store_coefficients_valid_from",
        "store_coefficients",
        ["valid_from"],
        unique=False,
    )
    op.create_index(
        "ix_store_coefficients_code",
        "store_coefficients",
        ["code"],
        unique=False,
    )


def downgrade() -> None:
    """
    Откат: сначала индексы, затем таблица.
    """
    op.drop_index("ix_store_coefficients_code", table_name="store_coefficients")
    op.drop_index("ix_store_coefficients_valid_from", table_name="store_coefficients")
    op.drop_index("ix_store_coefficients_store_id", table_name="store_coefficients")
    op.drop_table("store_coefficients")
