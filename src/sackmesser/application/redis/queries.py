"""Redis application queries."""

from pydantic import BaseModel, ConfigDict, Field


class GetCacheEntryQuery(BaseModel):
    """Fetch cache value from Redis."""

    model_config = ConfigDict(frozen=True)

    key: str = Field(min_length=1, max_length=200)
