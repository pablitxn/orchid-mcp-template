"""Domain entities for cache capability."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CacheEntry:
    """Represents a cache key projection."""

    key: str
    value: str | None
