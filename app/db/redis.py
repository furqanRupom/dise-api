import redis.asyncio as redis

from app.core.config import settings

# redis.from_url automatically creates and manages an underlying connection pool
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    max_connections=20,
)


async def get_redis() -> redis.Redis:
    """Dependency For FastAPI"""
    return redis_client
