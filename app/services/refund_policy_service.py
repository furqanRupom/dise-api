import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refund_policy import RefundPolicyTier
from app.schemas.refund_policy import RefundPolicyTierCreate, RefundPolicyTierUpdate


class RefundPolicyService:
    def __init__(self, db: Session):
        self.db = db

    def list_tiers(self, include_inactive: bool = False) -> list[RefundPolicyTier]:
        """List all refund policy tiers, optionally including inactive ones."""
        stmt = select(RefundPolicyTier).order_by(
            RefundPolicyTier.hours_before_pickup.desc
        )
        if not include_inactive:
            stmt = stmt.where(RefundPolicyTier.is_active.is_(True))
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_tier(self, tier_id: uuid.UUID) -> RefundPolicyTier:
        """Get a refund policy tier by hours before pickup."""
        refund_tier = (
            self.db.query(RefundPolicyTier)
            .filter(
                RefundPolicyTier.id == tier_id,
                RefundPolicyTier.is_active.is_(True),
                RefundPolicyTier.deleted_at.is_(None),
            )
            .first()
        )
        if not refund_tier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Refund tier not found"
            )
        return refund_tier

    def create_tier(self, payload: RefundPolicyTierCreate) -> RefundPolicyTier:
        """Create a new refund policy tier."""
        existing_tier = (
            self.db.query(RefundPolicyTier)
            .filter(
                RefundPolicyTier.hours_before_pickup == payload.hours_before_pickup,
                RefundPolicyTier.is_active.is_(True),
                RefundPolicyTier.deleted_at.is_(None),
            )
            .first()
        )
        if existing_tier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refund tier already exists",
            )
        refund_tier = RefundPolicyTier(**payload.model_dump())
        self.db.add(refund_tier)
        self.db.commit()
        self.db.refresh(refund_tier)
        return refund_tier

    def update_tier(
        self, tier_id: uuid.UUID, payload: RefundPolicyTierUpdate
    ) -> RefundPolicyTier:
        """Update a refund policy tier."""
        refund_tier = (
            self.db.query(RefundPolicyTier)
            .filter(
                RefundPolicyTier.id == tier_id,
                RefundPolicyTier.is_active.is_(True),
                RefundPolicyTier.deleted_at.is_(None),
            )
            .first()
        )
        if not refund_tier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Refund tier not found"
            )
        for key, value in payload.model_dump().items():
            setattr(refund_tier, key, value)
        self.db.commit()
        self.db.refresh(refund_tier)
        return refund_tier

    def delete_tier(self, tier_id: uuid.UUID) -> None:
        """Delete a refund policy tier."""
        refund_tier = (
            self.db.query(RefundPolicyTier)
            .filter(
                RefundPolicyTier.id == tier_id,
                RefundPolicyTier.is_active.is_(True),
                RefundPolicyTier.deleted_at.is_(None),
            )
            .first()
        )
        if not refund_tier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Refund tier not found"
            )
        refund_tier.is_active = False
        refund_tier.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
