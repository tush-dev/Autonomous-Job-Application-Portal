import hashlib
import json
import logging
from typing import Optional

from app.core.config import settings
from app.core.redis import redis_client

logger = logging.getLogger(__name__)


class AICache:
    KEY_PREFIX = "ai:cache:"
    DEFAULT_TTL = settings.AI_CACHE_TTL

    @classmethod
    def _make_key(cls, prompt: str, model: str) -> str:
        raw = f"{model}:{prompt.strip().lower()}"
        h = hashlib.sha256(raw.encode()).hexdigest()
        return f"{cls.KEY_PREFIX}{h}"

    @classmethod
    async def get(cls, prompt: str, model: str) -> Optional[str]:
        if not settings.AI_CACHE_ENABLED:
            return None
        key = cls._make_key(prompt, model)
        val = await redis_client.get(key)
        if val is not None:
            logger.info(f"AI cache hit: {key[:40]}...")
            return val
        return None

    @classmethod
    async def set(cls, prompt: str, model: str, response: str, ttl: Optional[int] = None) -> None:
        if not settings.AI_CACHE_ENABLED:
            return
        key = cls._make_key(prompt, model)
        ttl = ttl or cls.DEFAULT_TTL
        await redis_client.set(key, response, ex=ttl)
        logger.info(f"AI cache set: {key[:40]}... (ttl={ttl}s)")

    @classmethod
    async def invalidate(cls, prompt: str, model: str) -> None:
        key = cls._make_key(prompt, model)
        await redis_client.delete(key)
