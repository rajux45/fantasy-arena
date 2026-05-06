"""initial

Revision ID: 20260101_0000
Revises:
Create Date: 2026-01-01 00:00:00

This migration is intentionally empty. Use ``Base.metadata.create_all`` via
``python seed.py`` for local dev. For staging / prod, generate a real
auto-migration with ``alembic revision --autogenerate -m initial`` against your
target Postgres before first deploy.
"""
from __future__ import annotations

revision: str = "20260101_0000"
down_revision: str | None = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
