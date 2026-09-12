"""Business logic for vehicle bookings."""

import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BookingStatusHistory
from app.models.booking import Booking
from app.models.enums import BookingStatus
from app.models.location import Location
from app.models.maintenance import MaintenanceBlock
from app.models.vehicle import Vehicle
from app.schemas.booking import BookingCreate


class BookingService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_duration(self, start_date: date, end_date: date) -> int:
        """
        Calculate the rental duration in days.

        Booking dates use an exclusive end date.

        Examples:
            10 Sep -> 13 Sep = 3 rental days
            10 Sep -> 11 Sep = 1 rental day

        The caller should ensure that end_date is after start_date.
        """
        return (end_date - start_date).days

    def calculate_base_price(
        self,
        daily_rate: Decimal,
        start_date: date,
        end_date: date,
    ) -> Decimal:
        """
        Calculate the booking price before discounts.

        Base price = daily rental rate × rental duration.
        """
        duration = self.calculate_duration(start_date, end_date)

        return daily_rate * duration

    def calculate_total_price(
        self,
        base_price: Decimal,
        discount_amount: Decimal,
    ) -> Decimal:
        """
        Calculate the final booking price after applying a discount.

        The total can never be negative.
        """
        total = base_price - discount_amount

        return max(total, Decimal("0.00"))

    def get_vehicle(self, vehicle_id: uuid.UUID) -> Vehicle:
        """
        Fetch an active vehicle by ID.

        Soft-deleted vehicles are treated as not found because they
        should not be available for new bookings.
        """
        result = self.db.execute(
            select(Vehicle).where(
                Vehicle.id == vehicle_id,
                Vehicle.deleted_at.is_(None),
            )
        )

        vehicle = result.scalar_one_or_none()

        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found",
            )

        return vehicle

    def get_location(self, location_id: uuid.UUID) -> Location:
        """
        Fetch an active location by ID.

        Soft-deleted locations cannot be used for new bookings.
        """
        result = self.db.execute(
            select(Location).where(
                Location.id == location_id,
                Location.deleted_at.is_(None),
            )
        )

        location = result.scalar_one_or_none()

        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found",
            )

        return location

    def check_maintenance_conflict(
        self,
        vehicle_id: uuid.UUID,
        start_date: date,
        end_date: date,
    ) -> None:
        """
        Check whether the requested rental period overlaps
        an existing maintenance block.

        Booking and maintenance are stored in separate tables, so
        PostgreSQL cannot enforce this conflict using the booking
        exclusion constraint alone.

        The date range follows the same [start, end) convention
        used by the booking exclusion constraint.

        Example:
            Maintenance: 10 Sep -> 12 Sep
            Booking:     12 Sep -> 15 Sep

        These periods do NOT overlap.
        """
        result = self.db.execute(
            select(MaintenanceBlock.id).where(
                MaintenanceBlock.vehicle_id == vehicle_id,
                MaintenanceBlock.start_date < end_date,
                MaintenanceBlock.end_date > start_date,
            )
        )

        conflict = result.scalar_one_or_none()

        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vehicle is unavailable due to maintenance during the requested dates",
            )

    def determine_initial_status(
        self,
        vehicle: Vehicle,
    ) -> tuple[BookingStatus, datetime | None]:
        """
        Determine the initial booking status.

        Vehicles requiring owner/admin approval enter the
        pending_approval state and receive a 24-hour approval deadline.

        Other vehicles can proceed directly to payment.
        """
        if vehicle.requires_approval:
            return (
                BookingStatus.pending_approval,
                datetime.now(timezone.utc) + timedelta(hours=24),
            )

        return BookingStatus.pending_payment, None

    def create_booking(
        self,
        customer_id: uuid.UUID,
        payload: BookingCreate,
    ) -> Booking:
        """
        Create the initial booking.

        Flow:
            1. Validate the requested vehicle.
            2. Validate pickup and drop-off locations.
            3. Validate the rental date range.
            4. Check maintenance conflicts.
            5. Calculate price.
            6. Determine the initial booking status.
            7. Create the booking.
            8. Create the initial status-history record.
            9. Commit the transaction.
            10. Refresh and return the created booking.

        The PostgreSQL exclusion constraint remains the final
        database-level protection against concurrent overlapping
        confirmed/active bookings.
        """

        # Make sure the requested vehicle exists and is active.
        vehicle = self.get_vehicle(payload.vehicle_id)

        # Make sure both requested locations exist and are active.
        pickup_location = self.get_location(payload.pickup_location_id)
        dropoff_location = self.get_location(payload.dropoff_location_id)

        # A booking must contain at least one rental day.
        if payload.end_date <= payload.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date",
            )

        # A vehicle cannot be rented while it is blocked for maintenance.
        self.check_maintenance_conflict(
            vehicle_id=vehicle.id,
            start_date=payload.start_date,
            end_date=payload.end_date,
        )

        # Calculate the price using the vehicle's current daily rate.
        base_price = self.calculate_base_price(
            daily_rate=Decimal(str(vehicle.daily_rate)),
            start_date=payload.start_date,
            end_date=payload.end_date,
        )

        # Coupon/discount handling can be added here later.
        discount_amount = Decimal("0.00")

        total_price = self.calculate_total_price(
            base_price=base_price,
            discount_amount=discount_amount,
        )

        # Determine whether the booking needs approval before payment.
        booking_status, approval_deadline = self.determine_initial_status(vehicle)

        booking = Booking(
            customer_id=customer_id,
            vehicle_id=vehicle.id,
            pickup_location_id=pickup_location.id,
            dropoff_location_id=dropoff_location.id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            status=booking_status,
            base_price=base_price,
            discount_amount=discount_amount,
            total_price=total_price,
            currency=vehicle.currency,
            coupon_id=None,
            deposit_hold_amount=Decimal(str(vehicle.deposit_amount or 0)),
            approval_deadline=approval_deadline,
            created_by=customer_id,
        )

        self.db.add(booking)

        # Record the initial state transition for the booking.
        history = BookingStatusHistory(
            booking=booking,
            from_status=None,
            to_status=booking_status.value,
            changed_by=customer_id,
            reason="Booking created",
        )

        self.db.add(history)

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        # Refresh the instance so server-generated values such as
        # created_at are available on the returned object.
        self.db.refresh(booking)

        return booking
