"""Backward-compatible redis module exports (cache capability)."""

from sackmesser.application.cache import (
    CacheEntryDto,
    DeleteCacheEntryCommand,
    DeleteCacheEntryCommandHandler,
    DeleteCacheEntryHandler,
    DeleteCacheEntryResult,
    DeleteCacheEntryUseCase,
    GetCacheEntryHandler,
    GetCacheEntryQuery,
    GetCacheEntryQueryHandler,
    GetCacheEntryResult,
    GetCacheEntryUseCase,
    SetCacheEntryCommand,
    SetCacheEntryCommandHandler,
    SetCacheEntryHandler,
    SetCacheEntryResult,
    SetCacheEntryUseCase,
)

__all__ = [
    "CacheEntryDto",
    "DeleteCacheEntryCommand",
    "DeleteCacheEntryCommandHandler",
    "DeleteCacheEntryHandler",
    "DeleteCacheEntryResult",
    "DeleteCacheEntryUseCase",
    "GetCacheEntryHandler",
    "GetCacheEntryQuery",
    "GetCacheEntryQueryHandler",
    "GetCacheEntryResult",
    "GetCacheEntryUseCase",
    "SetCacheEntryCommand",
    "SetCacheEntryCommandHandler",
    "SetCacheEntryHandler",
    "SetCacheEntryResult",
    "SetCacheEntryUseCase",
]
