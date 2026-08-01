from fastapi import FastAPI, status

from app.api.auth import router as auth_router

app = FastAPI(
    title="Dise API",
    description="Backend API for the Dise project. Handles auth, users, and real-time features.",
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
)

app.include_router(auth_router)


@app.get("/", status_code=status.HTTP_200_OK)
async def hello():
    return {
        "statusCode": status.HTTP_200_OK,
        "message": "successfully running!",
        "docs": "/docs",
        "data": {"greetings": "Hello!"},
    }
