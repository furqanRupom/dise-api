"""add rented to vehicle status

Revision ID: b41b2677cfbd
Revises: 9aa439c38b01
Create Date: 2026-11-04 21:33:36.946802

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b41b2677cfbd"
down_revision: Union[str, Sequence[str], None] = "9aa439c38b01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE vehiclestatus ADD VALUE IF NOT EXISTS 'rented'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
