import uuid

from sqlalchemy import Boolean, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin


class RefundPolicyTier(Base, TimestampMixin, SoftDeleteMixin):
    """
    A tier is a threshold: if a cancellation happens at least
    `hours_before_pickup` hours before the booking start, `refund_percentage`
    applies. Multiple tiers form a step function (72h -> 100%, 24h -> 50%, 0h -> 0%).
    """

    __tablename__ = "refund_policy_tiers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    hours_before_pickup: Mapped[int] = mapped_column(Integer, nullable=False)
    refund_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
