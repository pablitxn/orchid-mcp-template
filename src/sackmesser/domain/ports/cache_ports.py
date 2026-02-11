"""Cache output ports (driven adapters)."""

from __future__ import annotations

from typing import Protocol

from sackmesser.domain.cache.entities import CacheEntry


class CacheRepositoryPort(Protocol):
    """Cache contract used by application handlers."""

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> bool:
        """Set a cache key."""

    async def get(self, key: str) -> CacheEntry:
        """Fetch cache value for key."""

    async def delete(self, key: str) -> bool:
        """Delete cache key."""
