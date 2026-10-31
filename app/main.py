import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.booking import router as booking_router
from app.api.coupon import router as coupon_router
from app.api.fleet import router as fleet_router
from app.api.location import router as location_router
from app.api.payment import router as payment_router
from app.api.refund_policy import router as refund_policy_router
from app.api.user import router as user_router
from app.api.vehicle import router as vehicle_router
from app.api.vehicle_category import router as vehicle_category_router
from app.api.webhooks import router as webhooks_router
from app.core.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events."""

    logger.info("Starting Dise API...")

    # Initialize resources here
    # Example:
    # await connect_database()
    # await connect_redis()

    yield

    logger.info("Shutting down Dise API...")


tags_metadata = [
    {"name": "Health", "description": "Check that the API is running."},
    {"name": "Auth", "description": "Register, login, logout and session handling."},
    {"name": "Users", "description": "User profiles and account management."},
    {"name": "Locations", "description": "Pickup and drop-off locations."},
    {"name": "Coupons", "description": "Create, validate and apply discount coupons."},
    {
        "name": "Vehicle Categories",
        "description": "Vehicle types such as sedan, SUV and van.",
    },
    {"name": "Vehicles", "description": "Browse and manage the vehicle catalog."},
    {"name": "Refund Policies", "description": "Cancellation and refund rules."},
    {"name": "Bookings", "description": "Create, view, modify and cancel bookings."},
    {"name": "Fleet", "description": "Admin tools for managing the fleet."},
    {"name": "Payments", "description": "Payments and refunds for bookings."},
]


app = FastAPI(
    title="Dise API",
    description=(
        "Backend REST API for **Dise**, a car rental platform. It covers the "
        "vehicle catalog, bookings, payments, coupons, and admin/fleet management.\n\n"
        "## Authentication\n"
        "Most endpoints require a login. Call `POST /auth/login` first. The JWT is "
        "stored in a cookie and sent automatically with later requests.\n\n"
        "## Roles\n"
        "- **Customer**: browse vehicles, book, pay\n"
        "- **Admin**: manage vehicles, fleet, coupons, refund policies\n\n"
        "## Responses\n"
        "Success and error responses follow a common format with `success`, "
        "`statusCode` and `message` fields."
    ),
    version="1.0.0",
    contact={
        "name": "Dise Engineering Team",
        "email": "engineering@dise.app",
    },
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    # only debug for development
    debug=True,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_HOST],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(location_router)
app.include_router(coupon_router)
app.include_router(vehicle_category_router)
app.include_router(vehicle_router)
app.include_router(refund_policy_router)
app.include_router(booking_router)
app.include_router(fleet_router)
app.include_router(payment_router)
app.include_router(webhooks_router)


@app.get(
    "/",
    tags=["Health"],
    summary="Health Check",
    description="Returns the current status of the API.",
    status_code=status.HTTP_200_OK,
)
async def health_check():
    """Health check endpoint."""

    return {
        "success": True,
        "statusCode": status.HTTP_200_OK,
        "message": "Dise API is running successfully.",
        "version": app.version,
        "documentation": {
            "swagger": app.docs_url,
            "redoc": app.redoc_url,
            "openapi": app.openapi_url,
        },
    }
