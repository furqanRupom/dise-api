"""Business logic for vehicle bookings."""

import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND

from app.models import BookingStatusHistory
from app.models.booking import Booking
from app.models.enums import BookingStatus
from app.models.location import Location
from app.models.maintenance import MaintenanceBlock
from app.models.vehicle import Vehicle
from app.schemas.booking import BookingCreate, BookingListParams


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

    def approve_booking(self, booking_id: uuid.UUID, changed_by: uuid.UUID) -> Booking:
        """Approve a pending booking before its approval deadline."""

        booking = self.get_booking(booking_id)

        if booking.status != BookingStatus.pending_approval:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only bookings pending approval can be approved",
            )
        now = datetime.now(timezone.utc)

        if booking.approval_deadline is not None and booking.approval_deadline <= now:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking approval deadline is expired!",
            )
        previous_status = booking.status

        booking.status = BookingStatus.pending_payment
        booking.approval_deadline = None

        history = BookingStatusHistory(
            booking=booking,
            from_status=previous_status.value,
            to_status=BookingStatus.pending_payment.value,
            changed_by=changed_by,
            reason="Booking approved",
        )

        self.db.add(history)

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()

        self.db.refresh(booking)
        return booking

    def reject_booking(self, booking_id: uuid.UUID, changed_by: uuid.UUID, reason: str):
        """Reject a pending booking and record the rejection reason."""

        booking = self.get_booking(booking_id)

        if booking.status != BookingStatus.pending_approval:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only bookings pending approval can be rejected",
            )

        reason = reason.strip()

        if not reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rejection reason is required.",
            )

        previous_status = booking.status

        booking.status = BookingStatus.rejected
        booking.approval_deadline = None

        history = BookingStatusHistory(
            booking=booking,
            from_status=previous_status.value,
            to_status=BookingStatus.rejected.value,
            changed_by=changed_by,
            reason=reason,
        )
        self.db.add(history)

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()

        self.db.refresh(booking)
        return booking

    def expire_pending_approvals(self) -> int:
        """Expire pending bookings whose approval deadline has passed."""

        now = datetime.now(timezone.utc)

        result = self.db.execute(
            select(Booking).where(
                Booking.status == BookingStatus.pending_approval,
                Booking.approval_deadline.is_not(None),
                Booking.approval_deadline <= now,
                Booking.deleted_at.is_(None),
            )
        )

        bookings = list(result.scalars().all())
        if not bookings:
            return 0

        for booking in bookings:
            booking.status = BookingStatus.expired
            booking.approval_deadline = None

            history = BookingStatusHistory(
                booking=booking,
                from_status=BookingStatus.pending_approval.value,
                to_status=BookingStatus.expired.value,
                changed_by=None,
                reason="Booking approval deadline expired",
            )
            self.db.add(history)

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        return len(bookings)

    def get_customer_bookings(
        self,
        customer_id: uuid.UUID,
        params: BookingListParams,
    ) -> tuple[list[Booking], int]:
        """Retrieve a paginated list of bookings for a customer."""

        query = select(Booking).where(
            Booking.customer_id == customer_id,
            Booking.deleted_at.is_(None),
        )

        count_query = (
            select(func.count())
            .select_from(Booking)
            .where(
                Booking.customer_id == customer_id,
                Booking.deleted_at.is_(None),
            )
        )

        # Filters
        if params.status is not None:
            query = query.where(Booking.status == params.status)
            count_query = count_query.where(Booking.status == params.status)

        if params.vehicle_id is not None:
            query = query.where(Booking.vehicle_id == params.vehicle_id)
            count_query = count_query.where(Booking.vehicle_id == params.vehicle_id)

        if params.pickup_location_id is not None:
            query = query.where(Booking.pickup_location_id == params.pickup_location_id)
            count_query = count_query.where(
                Booking.pickup_location_id == params.pickup_location_id
            )

        if params.dropoff_location_id is not None:
            query = query.where(
                Booking.dropoff_location_id == params.dropoff_location_id
            )
            count_query = count_query.where(
                Booking.dropoff_location_id == params.dropoff_location_id
            )

        if params.start_date_from is not None:
            query = query.where(Booking.start_date >= params.start_date_from)
            count_query = count_query.where(
                Booking.start_date >= params.start_date_from
            )

        if params.start_date_to is not None:
            query = query.where(Booking.start_date <= params.start_date_to)
            count_query = count_query.where(Booking.start_date <= params.start_date_to)

        if params.end_date_from is not None:
            query = query.where(Booking.end_date >= params.end_date_from)
            count_query = count_query.where(Booking.end_date >= params.end_date_from)

        if params.end_date_to is not None:
            query = query.where(Booking.end_date <= params.end_date_to)
            count_query = count_query.where(Booking.end_date <= params.end_date_to)

        if params.price_min is not None:
            query = query.where(Booking.total_price >= params.price_min)
            count_query = count_query.where(Booking.total_price >= params.price_min)

        if params.price_max is not None:
            query = query.where(Booking.total_price <= params.price_max)
            count_query = count_query.where(Booking.total_price <= params.price_max)

        # Sorting
        sort_column = {
            "created_at": Booking.created_at,
            "updated_at": Booking.updated_at,
            "start_date": Booking.start_date,
            "end_date": Booking.end_date,
            "total_price": Booking.total_price,
            "status": Booking.status,
        }[params.sort_by]

        if params.sort_order == "asc":
            query = query.order_by(
                sort_column.asc(),
                Booking.id.asc(),
            )
        else:
            query = query.order_by(
                sort_column.desc(),
                Booking.id.desc(),
            )

        # Pagination
        offset = (params.page - 1) * params.limit

        query = query.offset(offset).limit(params.limit)

        # Execute count query
        total = self.db.execute(count_query).scalar_one()

        # Execute bookings query
        bookings = list(self.db.execute(query).scalars().all())

        return bookings, total

    def get_customer_booking(
        self, customer_id: uuid.UUID, booking_id: uuid.UUID
    ) -> Booking:
        """Get Specific Booking for customer"""
        booking = self.db.execute(
            select(Booking).where(
                Booking.id == booking_id,
                Booking.customer_id == customer_id,
                Booking.deleted_at.is_(None),
            )
        ).scalar_one()

        if not booking:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        return booking

    def get_bookings(
        self,
        params: BookingListParams,
    ) -> tuple[list[Booking], int]:
        """Retrieve a paginated list of bookings for a Admin/Staff."""

        query = select(Booking).where(
            Booking.deleted_at.is_(None),
        )

        count_query = (
            select(func.count())
            .select_from(Booking)
            .where(
                Booking.deleted_at.is_(None),
            )
        )

        # Filters
        if params.status is not None:
            query = query.where(Booking.status == params.status)
            count_query = count_query.where(Booking.status == params.status)

        if params.vehicle_id is not None:
            query = query.where(Booking.vehicle_id == params.vehicle_id)
            count_query = count_query.where(Booking.vehicle_id == params.vehicle_id)

        if params.pickup_location_id is not None:
            query = query.where(Booking.pickup_location_id == params.pickup_location_id)
            count_query = count_query.where(
                Booking.pickup_location_id == params.pickup_location_id
            )

        if params.dropoff_location_id is not None:
            query = query.where(
                Booking.dropoff_location_id == params.dropoff_location_id
            )
            count_query = count_query.where(
                Booking.dropoff_location_id == params.dropoff_location_id
            )

        if params.start_date_from is not None:
            query = query.where(Booking.start_date >= params.start_date_from)
            count_query = count_query.where(
                Booking.start_date >= params.start_date_from
            )

        if params.start_date_to is not None:
            query = query.where(Booking.start_date <= params.start_date_to)
            count_query = count_query.where(Booking.start_date <= params.start_date_to)

        if params.end_date_from is not None:
            query = query.where(Booking.end_date >= params.end_date_from)
            count_query = count_query.where(Booking.end_date >= params.end_date_from)

        if params.end_date_to is not None:
            query = query.where(Booking.end_date <= params.end_date_to)
            count_query = count_query.where(Booking.end_date <= params.end_date_to)

        if params.price_min is not None:
            query = query.where(Booking.total_price >= params.price_min)
            count_query = count_query.where(Booking.total_price >= params.price_min)

        if params.price_max is not None:
            query = query.where(Booking.total_price <= params.price_max)
            count_query = count_query.where(Booking.total_price <= params.price_max)

        # Sorting
        sort_column = {
            "created_at": Booking.created_at,
            "updated_at": Booking.updated_at,
            "start_date": Booking.start_date,
            "end_date": Booking.end_date,
            "total_price": Booking.total_price,
            "status": Booking.status,
        }[params.sort_by]

        if params.sort_order == "asc":
            query = query.order_by(
                sort_column.asc(),
                Booking.id.asc(),
            )
        else:
            query = query.order_by(
                sort_column.desc(),
                Booking.id.desc(),
            )

        # Pagination
        offset = (params.page - 1) * params.limit

        query = query.offset(offset).limit(params.limit)

        # Execute count query
        total = self.db.execute(count_query).scalar_one()

        # Execute bookings query
        bookings = list(self.db.execute(query).scalars().all())

        return bookings, total

    def get_booking(self, booking_id: uuid.UUID) -> Booking:
        """Get Specific Booking for Admin/staff"""
        booking = self.db.execute(
            select(Booking).where(
                Booking.id == booking_id,
                Booking.deleted_at.is_(None),
            )
        ).scalar_one()

        if not booking:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        return booking
