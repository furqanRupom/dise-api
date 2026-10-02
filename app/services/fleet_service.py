"""app/services/fleet_service.py

Phase 4: vehicle hand-over (check-out) and return (check-in).

Terminology (fleet perspective):
    check_out = the vehicle leaves our hands  -> customer pickup
    check_in  = the vehicle comes back to us  -> customer return
"""

import uuid
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import (
    Booking,
    BookingStatusHistory,
    ConditionReport,
    User,
    Vehicle,
    VehicleStatus,
)
from app.models.condition_reports import ConditionReportImage
from app.models.enums import BookingStatus, ReportType, UserRole
from app.schemas.condition_reports import ConditionReportCreate
from app.services.booking_service import BookingService

# TODO : Will moved to settings (and also we need to update it booking service layer as well)
BUSINESS_TZ = ZoneInfo("Asia/Dhaka")


def business_today() -> date:
    return datetime.now(BUSINESS_TZ).date()


class FleetService:
    def __init__(self, db: Session):
        self.db = db
        self.booking_service = BookingService(db)

    # HELPERS
    def _lock_vehicle(self, vehicle_id: uuid.UUID):

        return self.db.execute(
            select(Vehicle)
            .where(Vehicle.id == vehicle_id)
            .with_for_update(of=Vehicle)
            .execution_options(populate_existing=True)
        ).scalar_one()

    def _get_report(self, booking_id: uuid.UUID, report_type: ReportType):

        return self.db.execute(
            select(ConditionReport).where(
                ConditionReport.booking_id == booking_id,
                ConditionReport.type == report_type,
            )
        ).scalar_one_or_none()

    def _add_report(
        self,
        booking: Booking,
        report_type: ReportType,
        staff_id: uuid.UUID,
        payload: ConditionReportCreate,
    ) -> ConditionReport:

        report = ConditionReport(
            booking_id=booking.id,
            type=report_type,
            odometer_km=payload.odometer_km,
            fuel_level_pct=payload.fuel_level_pct,
            notes=payload.notes.strip() if payload.notes else None,
            recorded_by=staff_id,
            images=[ConditionReportImage(image_url=url) for url in payload.image_urls],
        )
        self.db.add(report)
        return report

    def _add_history(
        self,
        booking: Booking,
        from_status: BookingStatus,
        to_status: BookingStatus,
        changed_by: uuid.UUID,
        reason: str,
    ):
        history = BookingStatusHistory(
            booking=booking,
            from_status=from_status.value,
            to_status=to_status.value,
            changed_by=changed_by,
            reason=reason,
        )
        self.db.add(history)
        return history

    def _commit(self):
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Conflicting update: the operation was already performed!",
            )
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def check_out(
        self, booking_id: uuid.UUID, staff_id: uuid.UUID, payload: ConditionReportCreate
    ):
        """
        Check-out(pick up) - Confirmed -> active
        """

        booking = self.booking_service.get_booking(booking_id, for_update=True)

        if booking.status != BookingStatus.confirmed:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only Confirmed bookings can be picked up",
            )

        today = business_today()

        if today < booking.start_date:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Pickup is not allowed before the booking start date",
            )

        if today >= booking.end_date:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking period has already ended",
            )

        # Lock the vehicle row. This also protects against handing the car
        # to a new renter while the previous one has not returned it yet
        # (the booking exclusion constraint cannot catch that).
        vehicle = self._lock_vehicle(booking.vehicle_id)

        if vehicle.status != VehicleStatus.available:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Vehicle cannot be handed over while {vehicle.status.value}",
            )

        self._add_report(booking, ReportType.check_out, staff_id, payload)

        booking.status = BookingStatus.active
        booking.actual_pickup_at = datetime.now(timezone.utc)
        booking.checked_out_by = staff_id
        vehicle.status = VehicleStatus.rented

        self._add_history(
            booking,
            BookingStatus.confirmed,
            BookingStatus.active,
            staff_id,
            "Vehicle handed over to customer",
        )

        self._commit()
        self.db.refresh(booking)
        return booking

    def check_in(
        self, booking_id: uuid.UUID, staff_id: uuid.UUID, payload: ConditionReportCreate
    ):
        booking = self.booking_service.get_booking(booking_id, for_update=True)

        if booking.status != BookingStatus.active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only active bookings can be returned",
            )

        pickup_report = self._get_report(booking_id, ReportType.check_out)

        if pickup_report is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Check out condition report is missing",
            )

        if payload.odometer_km < pickup_report.odometer_km:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Return odometer cannot be lower than pickup odometer",
            )

        vehicle = self._lock_vehicle(booking.vehicle_id)

        self._add_report(booking, ReportType.check_in, staff_id, payload)

        now = datetime.now(timezone.utc)
        booking.status = BookingStatus.completed
        booking.actual_return_at = now
        booking.checked_in_by = staff_id

        # Don't overwrite in_maintenance / retired if something else set it.
        if vehicle.status == VehicleStatus.rented:
            vehicle.status = VehicleStatus.available

        reason = "Vehicle returned"

        today = business_today()

        if today > booking.end_date:
            # Late Fee is phase 6 : we just only recorded here
            reason += " (late)"

        self._add_history(
            booking, BookingStatus.active, BookingStatus.completed, staff_id, reason
        )

        self._commit()
        self.db.refresh(booking)
        return booking

    def list_reports(self, booking_id: uuid.UUID, user: User) -> list[ConditionReport]:
        booking = self.booking_service.get_booking(booking_id)

        # Customers may only see reports for their own bookings; answer 404
        # (not 403) so booking ids can't be probed.
        if user.role == UserRole.customer and booking.customer_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        result = self.db.execute(
            select(ConditionReport)
            .where(ConditionReport.booking_id == booking.id)
            .order_by(ConditionReport.created_at.asc())
        )
        return list(result.scalars().all())
