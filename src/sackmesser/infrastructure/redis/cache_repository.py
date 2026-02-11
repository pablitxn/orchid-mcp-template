"""Redis repository adapter for cache examples."""

from __future__ import annotations

from orchid_commons import RedisCache

from sackmesser.domain.ports.redis_ports import CacheRepositoryPort
from sackmesser.domain.redis.entities import CacheEntry


class RedisCacheRepository(CacheRepositoryPort):
    """Adapt commons RedisCache to domain cache port."""

    def __init__(self, cache: RedisCache) -> None:
        self._cache = cache

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> bool:
        return await self._cache.set(key, value, ttl_seconds=ttl_seconds)

    async def get(self, key: str) -> CacheEntry:
        value = await self._cache.get(key)
        if isinstance(value, bytes):
            return CacheEntry(key=key, value=value.decode("utf-8"))
        if value is None:
            return CacheEntry(key=key, value=None)
        return CacheEntry(key=key, value=str(value))

    async def delete(self, key: str) -> bool:
        return bool(await self._cache.delete(key))
