# app/api/routes/fleet.py
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, require_staff
from app.db import get_db
from app.models.user import User
from app.schemas.booking import BookingResponse
from app.schemas.condition_reports import ConditionReportCreate, ConditionReportRead
from app.services.fleet_service import FleetService

router = APIRouter(prefix="/v1/booking", tags=["fleet"])


@router.post("/{booking_id}/check-out", response_model=BookingResponse)
def check_out_booking(
    booking_id: uuid.UUID,
    payload: ConditionReportCreate,
    db: Annotated[Session, Depends(get_db)],
    staff: Annotated[User, Depends(require_staff)],
):
    """Hand the vehicle to the customer: confirmed -> active."""
    service = FleetService(db)
    return service.check_out(booking_id, staff.id, payload)


@router.post("/{booking_id}/check-in", response_model=BookingResponse)
def check_in_booking(
    booking_id: uuid.UUID,
    payload: ConditionReportCreate,
    db: Annotated[Session, Depends(get_db)],
    staff: Annotated[User, Depends(require_staff)],
):
    """Receive the vehicle back: active -> completed."""

    service = FleetService(db)
    return service.check_in(booking_id, staff.id, payload)


@router.get("/{booking_id}/condition-reports", response_model=list[ConditionReportRead])
def list_condition_reports(
    booking_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_active_user)],
):
    service = FleetService(db)
    return service.list_reports(booking_id, user)
