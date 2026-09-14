"""Booking API endpoints.

This module contains booking endpoints for customers, staff, and admins.
As the booking domain grows, these endpoints can be separated into
role-specific routers to keep the API easier to maintain.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from starlette.status import HTTP_200_OK

from app.core.dependencies import require_user
from app.db import get_db
from app.models.user import User
from app.schemas.booking import (
    BookingCreate,
    BookingListParams,
    BookingListResponse,
    BookingResponse,
)
from app.services.booking_service import BookingService

router = APIRouter(
    prefix="/v1/booking",
    tags=["booking"],
)


@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new booking",
    description=(
        "Create a vehicle booking for the currently authenticated user.\n\n"
        "The customer is determined from the authentication context, so "
        "`customer_id` does not need to be included in the request body.\n\n"
        "The booking service validates the vehicle, pickup and drop-off "
        "locations, rental dates, and maintenance conflicts before creating "
        "the booking.\n\n"
        "Rental dates use an exclusive end date. For example, a booking "
        "from `2026-09-15` to `2026-09-18` represents 3 rental days.\n\n"
        "The initial booking status depends on whether the selected vehicle "
        "requires approval."
    ),
    responses={
        201: {
            "description": "Booking created successfully.",
        },
        400: {
            "description": "Invalid rental dates.",
        },
        401: {
            "description": "Authentication is required.",
        },
        404: {
            "description": "Vehicle or location was not found.",
        },
        409: {
            "description": "The vehicle is unavailable during the requested dates.",
        },
    },
)
async def create_booking(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(require_user),
    ],
    payload: BookingCreate,
):
    """Create a new vehicle booking for the authenticated customer.

    Args:
        db: Database session provided by the dependency.
        current_user: Authenticated user creating the booking.
        payload: Vehicle, locations, rental dates, and optional coupon.

    Returns:
        The newly created booking.

    Raises:
        HTTPException:
            - 400 if the rental date range is invalid.
            - 401 if the user is not authenticated.
            - 404 if the vehicle or location does not exist.
            - 409 if the vehicle conflicts with maintenance.

    Notes:
        The service layer is responsible for business rules such as
        duration calculation, pricing, maintenance availability, initial
        booking status, approval deadlines, and status history creation.
    """
    booking_service = BookingService(db)

    return booking_service.create_booking(
        customer_id=current_user.id,
        payload=payload,
    )


@router.get(
    "/my",
    response_model=BookingListResponse,
    status_code=HTTP_200_OK,
    summary="List my bookings",
    description=(
        "Return paginated bookings belonging to the currently "
        "authenticated customer. Supports filtering and sorting."
    ),
)
async def get_my_bookings(
    db: Annotated[Session, Depends(get_db)],
    params: Annotated[BookingListParams, Depends()],
    current_user: Annotated[User, Depends(require_user)],
):
    """Return the authenticated customer's bookings."""

    booking_service = BookingService(db)

    bookings, total = booking_service.get_customer_bookings(
        current_user.id,
        params,
    )

    total_pages = (total + params.limit - 1) // params.limit if total > 0 else 0

    return BookingListResponse(
        items=bookings,
        page=params.page,
        limit=params.limit,
        total=total,
        total_pages=total_pages,
        has_previous=params.page > 1,
        has_next=params.page < total_pages,
    )
