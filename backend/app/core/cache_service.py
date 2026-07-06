import json
from typing import Any, Optional

from app.core.redis import redis_client


class CacheService:
    async def get(self, key: str) -> Optional[Any]:
        val = await redis_client.get(key)
        if val is not None:
            try:
                return json.loads(val)
            except (json.JSONDecodeError, TypeError):
                return val
        return None

    async def set(self, key: str, value: Any, expire: int = 300) -> None:
        val = json.dumps(value, default=str)
        await redis_client.set(key, val, ex=expire)

    async def delete(self, key: str) -> None:
        await redis_client.delete(key)

    async def exists(self, key: str) -> bool:
        return await redis_client.exists(key) > 0