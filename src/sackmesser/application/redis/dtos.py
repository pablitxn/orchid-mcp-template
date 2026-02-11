"""Backward-compatible cache DTO exports."""

from sackmesser.application.cache.dtos import (
    CacheEntryDto,
    DeleteCacheEntryResult,
    GetCacheEntryResult,
    SetCacheEntryResult,
)

__all__ = [
    "CacheEntryDto",
    "DeleteCacheEntryResult",
    "GetCacheEntryResult",
    "SetCacheEntryResult",
]
