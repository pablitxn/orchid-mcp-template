"""Domain entities for Redis-backed cache examples."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CacheEntry:
    """Represents a cache key/value projection."""

    key: str
    value: str | None
