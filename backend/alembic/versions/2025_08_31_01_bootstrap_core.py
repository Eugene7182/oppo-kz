# -*- coding: utf-8 -*-
"""bootstrap core tables: users, stores, skus, bonus_grids"""

from alembic import op

# Эта миграция идёт сразу ПОСЛЕ userrole
revision = "2025_08_31_01_bootstrap_core"
down_revision = "2025_08_31_add_supervisor_role"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users: используем уже существующий ENUM userrole
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE,
            hashed_password VARCHAR(255),
            role userrole NOT NULL DEFAULT 'office',
            created_at TIMESTAMP NOT NULL DEFAULT now()
        );
        """
    )

    # stores: минимальный справочник
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS stores (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            code VARCHAR(32) UNIQUE,
            city VARCHAR(100),
            created_at TIMESTAMP NOT NULL DEFAULT now()
        );
        """
    )

    # skus: минимальный справочник
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS skus (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            code VARCHAR(64) UNIQUE,
            memory_option VARCHAR(50),
            created_at TIMESTAMP NOT NULL DEFAULT now()
        );
        """
    )

    # bonus_grids: нужна для FK в бонусных правилах перевыполнения
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS bonus_grids (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            effective_from DATE NOT NULL DEFAULT CURRENT_DATE,
            active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP NOT NULL DEFAULT now()
        );
        """
    )


def downgrade() -> None:
    # Откатывать базовые таблицы небезопасно (зависимости последующих миграций),
    # поэтому оставляем no-op.
    pass
