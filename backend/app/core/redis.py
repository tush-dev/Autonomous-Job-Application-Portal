import redis.asyncio as redis

from app.core.config import settings

redis_client: redis.Redis = redis.from_url(
    str(settings.REDIS_URL),
    decode_responses=True,
)


async def get_redis() -> redis.Redis:
    return redis_client


async def close_redis():
    await redis_client.close()
