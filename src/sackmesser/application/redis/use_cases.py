"""Backward-compatible aliases for legacy cache use-case names."""

from sackmesser.application.cache.handlers import (
    DeleteCacheEntryUseCase,
    GetCacheEntryUseCase,
    SetCacheEntryUseCase,
)

__all__ = [
    "DeleteCacheEntryUseCase",
    "GetCacheEntryUseCase",
    "SetCacheEntryUseCase",
]
