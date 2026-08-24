import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.coupon import router as coupon_router
from app.api.location import router as location_router
from app.api.user import router as user_router
from app.api.vehicle_category import router as vehicle_category_router
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

    # Clean up resources here
    # Example:
    # await disconnect_redis()
    # await disconnect_database()


app = FastAPI(
    title="Dise API",
    description=(
        "Backend API for the Dise project. "
        "Provides authentication, user management, and other core services."
    ),
    version="1.0.0",
    contact={
        "name": "Dise Team",
        "url": "https://your-domain.com",
        "email": "support@your-domain.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
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
