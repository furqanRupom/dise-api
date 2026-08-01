from redis.asyncio import ConnectionPool, Redis

from app.core.settings import settings

pool = ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
    max_connections=20,
)

# Global Redis Client
redis_client = Redis(connection_pool=pool)


async def get_redis() -> Redis:
    """Dependency For FastAPI"""
    return redis_client
