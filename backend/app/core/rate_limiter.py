from app.core.redis import redis_client
from app.core.config import settings


async def check_rate_limit(
    key: str,
    max_requests: int,
    window_seconds: int = 60,
) -> tuple[bool, int, int]:
    if not settings.RATE_LIMIT_ENABLED:
        return True, max_requests, 0

    now = __import__("time").time()
    window_start = int(now - window_start if (window_start := now - window_seconds) else 0)

    pipeline = redis_client.pipeline()
    pipeline.zadd(key, {str(now): now})
    pipeline.zremrangebyscore(key, 0, now - window_seconds)
    pipeline.zcard(key)
    pipeline.expire(key, window_seconds)
    results = await pipeline.execute()

    current_count = results[2]
    remaining = max(0, max_requests - current_count)
    reset_time = int(now) + window_seconds

    return current_count <= max_requests, remaining, reset_time
