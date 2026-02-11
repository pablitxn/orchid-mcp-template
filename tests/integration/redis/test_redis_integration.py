"""Redis integration tests against local docker instance."""

from __future__ import annotations

import pytest
from orchid_commons import RedisCache, RedisSettings

from sackmesser.infrastructure.redis.cache_repository import RedisCacheRepository


@pytest.mark.integration
async def test_redis_cache_repository_integration() -> None:
    cache: RedisCache | None = None
    try:
        cache = await RedisCache.create(
            RedisSettings(
                url="redis://localhost:6379/0",
                key_prefix="sackmesser-it",
                default_ttl_seconds=60,
            )
        )
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"Redis not available: {exc}")

    try:
        repository = RedisCacheRepository(cache)
        assert await repository.set("hello", "world") is True
        found = await repository.get("hello")
        deleted = await repository.delete("hello")

        assert found.value == "world"
        assert deleted is True
    finally:
        await cache.close()
