"""add users table

Revision ID: 26cf8501a8f8
Revises: 0174af76d98a
Create Date: 2026-03-25 19:44:48.382212

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "26cf8501a8f8"
down_revision = "0174af76d98a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("users")}
    if "verified_at" in existing_columns:
        op.alter_column(
            "users",
            "verified_at",
            existing_type=sa.TIMESTAMP(),
            type_=sa.DateTime(),
            existing_nullable=True,
        )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("users")}
    if "verified_at" in existing_columns:
        op.alter_column(
            "users",
            "verified_at",
            existing_type=sa.DateTime(),
            type_=sa.TIMESTAMP(),
            existing_nullable=True,
        )
