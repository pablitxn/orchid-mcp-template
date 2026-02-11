"""Unit tests for Redis cache repository adapter."""

from __future__ import annotations

from sackmesser.infrastructure.db.redis.cache_repository import RedisCacheRepository


class _FakeRedisCache:
    def __init__(self) -> None:
        self.set_calls: list[tuple[str, str, int | None]] = []
        self.get_calls: list[str] = []
        self.delete_calls: list[str] = []
        self.store: dict[str, object] = {}
        self.delete_return: object = 1

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> bool:
        self.set_calls.append((key, value, ttl_seconds))
        self.store[key] = value
        return True

    async def get(self, key: str) -> object:
        self.get_calls.append(key)
        return self.store.get(key)

    async def delete(self, key: str) -> object:
        self.delete_calls.append(key)
        return self.delete_return


async def test_set_delegates_to_cache() -> None:
    cache = _FakeRedisCache()
    repository = RedisCacheRepository(cache)  # type: ignore[arg-type]

    result = await repository.set("alpha", "1", ttl_seconds=30)

    assert result is True
    assert cache.set_calls == [("alpha", "1", 30)]


async def test_get_decodes_bytes_value() -> None:
    cache = _FakeRedisCache()
    cache.store["alpha"] = b"1"
    repository = RedisCacheRepository(cache)  # type: ignore[arg-type]

    entry = await repository.get("alpha")

    assert entry.key == "alpha"
    assert entry.value == "1"


async def test_get_returns_none_when_missing() -> None:
    cache = _FakeRedisCache()
    repository = RedisCacheRepository(cache)  # type: ignore[arg-type]

    entry = await repository.get("missing")

    assert entry.key == "missing"
    assert entry.value is None


async def test_get_coerces_non_string_values() -> None:
    cache = _FakeRedisCache()
    cache.store["alpha"] = 123
    repository = RedisCacheRepository(cache)  # type: ignore[arg-type]

    entry = await repository.get("alpha")

    assert entry.value == "123"


async def test_delete_casts_result_to_bool() -> None:
    cache = _FakeRedisCache()
    repository = RedisCacheRepository(cache)  # type: ignore[arg-type]

    cache.delete_return = 0
    first = await repository.delete("alpha")
    cache.delete_return = 2
    second = await repository.delete("alpha")

    assert first is False
    assert second is True
    assert cache.delete_calls == ["alpha", "alpha"]
