"""Payment endpoints.

ADAPT THESE IMPORTS to your project: get_db and get_current_user.
Handlers are plain `def` (not async) on purpose: PaymentService is synchronous
and makes blocking Stripe calls, so FastAPI runs them in its threadpool.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    require_admin_or_support,
    require_staff,
    require_user,
)
from app.db.database import get_db
from app.models import User
from app.models.enums import PaymentStatus, PaymentType, UserRole
from app.schemas.payment import (
    DepositCaptureRequest,
    PaymentListResponse,
    PaymentOut,
    PayResponse,
)
from app.services.payment_service import PaymentService

router = APIRouter(tags=["payments"])


# ---- customer ------------------------------------------------------------ #
@router.post("/bookings/{booking_id}/pay", response_model=PayResponse)
def pay_booking(
    booking_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """Create (or reuse) the PaymentIntent. Booking is confirmed by webhook."""
    service = PaymentService(db)
    return service.start_charge(user.id, booking_id)


@router.post("/bookings/{booking_id}/deposit", response_model=PayResponse)
def authorize_deposit(
    booking_id: uuid.UUID,
    user: Annotated[User, Depends(require_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Card hold for the security deposit (manual capture)."""
    service = PaymentService(db)
    return service.start_deposit_hold(user.id, booking_id)


@router.get("/bookings/{booking_id}/payments", response_model=list[PaymentOut])
def booking_payments(
    booking_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    service = PaymentService(db)
    return service.list_payments(booking_id, user)


# ---- fleet staff --------------------------------------------------------- #
@router.post("/bookings/{booking_id}/deposit/capture", response_model=PaymentOut)
def capture_deposit(
    booking_id: uuid.UUID,
    body: DepositCaptureRequest,
    _: Annotated[User, Depends(require_staff)],
    db: Annotated[Session, Depends(get_db)],
):
    """Keep all or part of the deposit (damage, fuel, ...). One-shot."""
    service = PaymentService(db)
    return service.capture_deposit(booking_id, body.amount, body.reason)


@router.post("/bookings/{booking_id}/deposit/release", response_model=PaymentOut)
def release_deposit(
    booking_id: uuid.UUID,
    _: Annotated[User, Depends(require_staff)],
    db: Annotated[Session, Depends(get_db)],
):
    """Clean return: release the hold."""
    service = PaymentService(db)
    return service.release_deposit(booking_id)


# ---- admin / support ----------------------------------------------------- #
@router.get("/admin/payments", response_model=PaymentListResponse)
def admin_payments(
    _: Annotated[User, Depends(require_admin_or_support)],
    db: Annotated[Session, Depends(get_db)],
    payment_type: Annotated[PaymentType | None, Query(alias="type")] = None,
    payment_status: Annotated[PaymentStatus | None, Query(alias="status")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """Reconciliation view, e.g. ?type=refund&status=failed."""
    service = PaymentService(db)
    items, total = service.admin_list_payments(
        payment_type, payment_status, page, limit
    )
    return PaymentListResponse(
        items=[PaymentOut.model_validate(p) for p in items],
        total=total,
        page=page,
        limit=limit,
    )
