"""Cache request/response models."""

from pydantic import BaseModel, ConfigDict, Field


class SetCacheEntryCommand(BaseModel):
    """Write cache value."""

    model_config = ConfigDict(frozen=True)

    key: str = Field(min_length=1, max_length=200)
    value: str = Field(min_length=1)
    ttl_seconds: int | None = Field(default=None, ge=1)


class DeleteCacheEntryCommand(BaseModel):
    """Delete cache value."""

    model_config = ConfigDict(frozen=True)

    key: str = Field(min_length=1, max_length=200)


class GetCacheEntryQuery(BaseModel):
    """Fetch cache value by key."""

    model_config = ConfigDict(frozen=True)

    key: str = Field(min_length=1, max_length=200)


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
