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
    RefundPolicyTierOut,
    RefundPolicyTierUpdate,
    RefundQuoteRequest,
    RefundQuoteResponse,
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


@router.post("/", response_model=RefundPolicyTierOut)
async def create_refund_policy(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
    tier: RefundPolicyTierCreate,
):
    service = RefundPolicyService(db)
    return service.create_tier(tier)


@router.put("/{tier_id}", response_model=RefundPolicyTierOut)
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


@router.post("/quote", response_model=RefundQuoteResponse)
async def quote_refund(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
    payload: RefundQuoteRequest,
):
    service = RefundPolicyService(db)
    pct, tier_id = await service.compute_refund_percentage(payload.hours_until_pickup)
    return RefundQuoteResponse(
        hours_until_pickup=payload.hours_until_pickup,
        refund_percentage=pct,
        matched_tier_id=tier_id,
    )
