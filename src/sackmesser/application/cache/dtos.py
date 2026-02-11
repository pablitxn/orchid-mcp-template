"""Cache response DTOs."""

from pydantic import BaseModel, ConfigDict


class CacheEntryDto(BaseModel):
    """Cache key/value projection for adapters."""

    model_config = ConfigDict(frozen=True)

    key: str
    value: str | None
    found: bool


class SetCacheEntryResult(BaseModel):
    """Result wrapper for cache set."""

    model_config = ConfigDict(frozen=True)

    success: bool
    key: str


class DeleteCacheEntryResult(BaseModel):
    """Result wrapper for cache delete."""

    model_config = ConfigDict(frozen=True)

    success: bool
    key: str


class GetCacheEntryResult(BaseModel):
    """Result wrapper for cache get."""

    model_config = ConfigDict(frozen=True)

    entry: CacheEntryDto
