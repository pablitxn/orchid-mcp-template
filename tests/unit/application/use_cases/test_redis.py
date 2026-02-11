"""Unit tests for cache request handlers."""

from __future__ import annotations

from sackmesser.application.handlers.cache import (
    DeleteCacheEntryCommandHandler,
    GetCacheEntryQueryHandler,
    SetCacheEntryCommandHandler,
)
from sackmesser.application.requests.cache import (
    DeleteCacheEntryCommand,
    GetCacheEntryQuery,
    SetCacheEntryCommand,
)
from sackmesser.domain.cache import CacheEntry


class _FakeCacheRepository:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> bool:
        del ttl_seconds
        self._store[key] = value
        return True

    async def get(self, key: str) -> CacheEntry:
        return CacheEntry(key=key, value=self._store.get(key))

    async def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None


async def test_set_and_get_cache_handlers() -> None:
    repository = _FakeCacheRepository()

    set_result = await SetCacheEntryCommandHandler(repository).handle(
        SetCacheEntryCommand(key="alpha", value="1")
    )
    get_result = await GetCacheEntryQueryHandler(repository).handle(
        GetCacheEntryQuery(key="alpha")
    )

    assert set_result.success is True
    assert get_result.entry.found is True
    assert get_result.entry.value == "1"


async def test_delete_cache_handler() -> None:
    repository = _FakeCacheRepository()
    await repository.set("alpha", "1")

    result = await DeleteCacheEntryCommandHandler(repository).handle(
        DeleteCacheEntryCommand(key="alpha")
    )
    assert result.success is True
