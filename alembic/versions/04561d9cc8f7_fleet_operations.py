"""fleet operations

Revision ID: 04561d9cc8f7
Revises: 990f8a4dd8d1
Create Date: 2026-09-30 15:46:03.323593

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "04561d9cc8f7"
down_revision: Union[str, Sequence[str], None] = "990f8a4dd8d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ADD VALUE cannot run inside the migration's transaction block.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE vehiclestatus ADD VALUE IF NOT EXISTS 'rented'")

    op.add_column(
        "bookings",
        sa.Column("actual_pickup_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "bookings",
        sa.Column("actual_return_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("bookings", sa.Column("checked_in_by", sa.Uuid(), nullable=True))
    op.add_column("bookings", sa.Column("checked_out_by", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_bookings_checked_in_by_users",
        "bookings",
        "users",
        ["checked_in_by"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_bookings_checked_out_by_users",
        "bookings",
        "users",
        ["checked_out_by"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_unique_constraint(
        "uq_condition_reports_booking_type", "condition_reports", ["booking_id", "type"]
    )
    op.create_check_constraint("ck_vehicles_odometer", "vehicles", "odometer_km >= 0")


def downgrade() -> None:
    op.drop_constraint("ck_vehicles_odometer", "vehicles", type_="check")
    op.drop_constraint(
        "uq_condition_reports_booking_type", "condition_reports", type_="unique"
    )
    op.drop_constraint(
        "fk_bookings_checked_out_by_users", "bookings", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_bookings_checked_in_by_users", "bookings", type_="foreignkey"
    )
    op.drop_column("bookings", "checked_out_by")
    op.drop_column("bookings", "checked_in_by")
    op.drop_column("bookings", "actual_return_at")
    op.drop_column("bookings", "actual_pickup_at")
    # Postgres cannot drop an enum value; 'rented' stays in the type.
