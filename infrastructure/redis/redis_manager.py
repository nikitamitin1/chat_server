from __future__ import annotations
import os, json, aioredis
from typing import Any, Iterable

class RedisManager:
    """Tiny async wrapper around aioredis with JSON helpers."""

    def __init__(self, dsn: str | None = None):
        self._dsn = dsn or os.getenv("REDIS_URL", "redis://localhost:6379")
        self._redis: aioredis.Redis | None = None

    async def connect(self) -> None:
        if self._redis is None:
            self._redis = await aioredis.from_url(self._dsn, decode_responses=True)

    async def close(self) -> None:
        if self._redis:
            await self._redis.close()

    # --------------- key/value JSON --------------------------------------
    async def set_json(self, key: str, value: Any, ex: int | None = None) -> None:
        await self._redis.set(key, json.dumps(value), ex=ex)

    async def get_json(self, key: str) -> Any | None:
        v = await self._redis.get(key)
        return json.loads(v) if v else None

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

    # --------------- sets (for chat membership & presence) ---------------
    async def sadd(self, key: str, *members: str) -> None:
        await self._redis.sadd(key, *members)

    async def srem(self, key: str, *members: str) -> None:
        await self._redis.srem(key, *members)

    async def smembers(self, key: str) -> set[str]:
        return await self._redis.smembers(key)

    async def expire(self, key: str, ttl: int) -> None:
        await self._redis.expire(key, ttl)

