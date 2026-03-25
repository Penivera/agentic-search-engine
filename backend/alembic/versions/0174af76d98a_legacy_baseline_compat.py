"""legacy baseline compatibility revision

Revision ID: 0174af76d98a
Revises:
Create Date: 2026-03-25 22:30:00.000000

"""

# revision identifiers, used by Alembic.
revision = "0174af76d98a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """No-op compatibility baseline for existing databases."""


def downgrade() -> None:
    """No-op downgrade for compatibility baseline."""
