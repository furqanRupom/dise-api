"""add expired booking status

Revision ID: 06b9c9a18716
Revises: 7dc3b139775b
Create Date: 2026-09-17 20:16:37.560381

"""

from typing import Sequence, Union

from alembic import op

revision: str = "06b9c9a18716"
down_revision: Union[str, Sequence[str], None] = "7dc3b139775b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE bookingstatus ADD VALUE IF NOT EXISTS 'expired'")


def downgrade() -> None:
    # PostgreSQL does not support removing an enum value directly.
    pass
