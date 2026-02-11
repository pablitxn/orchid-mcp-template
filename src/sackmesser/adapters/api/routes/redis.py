"""Redis cache API routes."""

from fastapi import APIRouter, HTTPException, Path, status
from pydantic import BaseModel, Field

from sackmesser.adapters.dependencies import ContainerDep
from sackmesser.application.redis import (
    DeleteCacheEntryCommand,
    GetCacheEntryQuery,
    SetCacheEntryCommand,
)

router = APIRouter(prefix="/api/v1/cache")


class SetCacheRequest(BaseModel):
    """Request body for cache set operation."""

    value: str = Field(min_length=1)
    ttl_seconds: int | None = Field(default=None, ge=1)


@router.put("/{key}")
async def set_cache(
    body: SetCacheRequest,
    container: ContainerDep,
    key: str = Path(min_length=1, max_length=200),
) -> dict[str, object]:
    """Set cache entry in Redis."""
    handler = container.set_cache_entry_handler
    if handler is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Redis module is disabled",
        )

    result = await handler.handle(
        SetCacheEntryCommand(key=key, value=body.value, ttl_seconds=body.ttl_seconds)
    )
    return result.model_dump()


@router.get("/{key}")
async def get_cache(
    container: ContainerDep,
    key: str = Path(min_length=1, max_length=200),
) -> dict[str, object]:
    """Get cache entry from Redis."""
    handler = container.get_cache_entry_handler
    if handler is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Redis module is disabled",
        )

    result = await handler.handle(GetCacheEntryQuery(key=key))
    payload = result.model_dump()
    if not result.entry.found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=payload)
    return payload


@router.delete("/{key}")
async def delete_cache(
    container: ContainerDep,
    key: str = Path(min_length=1, max_length=200),
) -> dict[str, object]:
    """Delete cache entry from Redis."""
    handler = container.delete_cache_entry_handler
    if handler is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Redis module is disabled",
        )

    result = await handler.handle(DeleteCacheEntryCommand(key=key))
    return result.model_dump()
