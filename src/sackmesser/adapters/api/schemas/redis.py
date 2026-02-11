"""Schemas for Redis cache routes."""

from pydantic import BaseModel, Field


class SetCacheRequest(BaseModel):
    """Request body for cache set operation."""

    value: str = Field(min_length=1)
    ttl_seconds: int | None = Field(default=None, ge=1)
