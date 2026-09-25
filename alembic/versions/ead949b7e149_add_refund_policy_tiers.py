"""add refund policy tiers

Revision ID: ead949b7e149
Revises: 06b9c9a18716
Create Date: 2026-09-25 23:37:04.405588

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ead949b7e149"
down_revision: Union[str, Sequence[str], None] = "06b9c9a18716"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
