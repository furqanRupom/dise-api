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

API_V1_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Dise API...")
    yield
    logger.info("Shutting down Dise API...")


app = FastAPI(
    title="Dise API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=True,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_HOST],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(user_router, prefix=API_V1_PREFIX)
app.include_router(location_router, prefix=API_V1_PREFIX)
app.include_router(coupon_router, prefix=API_V1_PREFIX)
app.include_router(vehicle_category_router, prefix=API_V1_PREFIX)
app.include_router(vehicle_router, prefix=API_V1_PREFIX)
app.include_router(refund_policy_router, prefix=API_V1_PREFIX)
app.include_router(booking_router, prefix=API_V1_PREFIX)
app.include_router(fleet_router, prefix=API_V1_PREFIX)
app.include_router(payment_router, prefix=API_V1_PREFIX)
app.include_router(webhooks_router, prefix=API_V1_PREFIX)


# Health Check
@app.get(
    "/",
    tags=["Health"],
    summary="Health Check",
    description="Check whether the Dise API is running.",
    status_code=status.HTTP_200_OK,
)
async def health_check():
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
