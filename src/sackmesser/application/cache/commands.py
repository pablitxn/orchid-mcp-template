"""Cache command models."""

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
