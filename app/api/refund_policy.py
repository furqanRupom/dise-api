"""Refund policy API endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db import get_db
from app.models import User
from app.models.refund_policy import RefundPolicyTier
from app.schemas.refund_policy import (
    RefundPolicyTierCreate,
    RefundPolicyTierUpdate,
)
from app.services.refund_policy_service import RefundPolicyService

router = APIRouter(
    prefix="/refund-policy",
    tags=["refund-policy"],
)


@router.get("/", response_model=list[RefundPolicyTier])
async def get_refund_policy(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
    include_inactive: bool = False,
):
    service = RefundPolicyService(db)
    return service.list_tiers(include_inactive=include_inactive)


@router.post("/", response_model=RefundPolicyTier)
async def create_refund_policy(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
    tier: RefundPolicyTierCreate,
):
    service = RefundPolicyService(db)
    return service.create_tier(tier)


@router.put("/{tier_id}", response_model=RefundPolicyTier)
async def update_refund_policy(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
    tier_id: uuid.UUID,
    tier: RefundPolicyTierUpdate,
):
    service = RefundPolicyService(db)
    return service.update_tier(tier_id, tier)


@router.delete("/{tier_id}", response_model=None)
async def delete_refund_policy(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
    tier_id: uuid.UUID,
):
    service = RefundPolicyService(db)
    return service.delete_tier(tier_id)
