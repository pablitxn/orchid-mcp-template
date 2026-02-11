"""Redis cache API routes."""

from fastapi import APIRouter, Path

from sackmesser.adapters.dependencies import ContainerDep
from sackmesser.adapters.api.schemas import SetCacheRequest
from sackmesser.application.errors import DisabledModuleError, NotFoundError
from sackmesser.application.cache import (
    DeleteCacheEntryCommand,
    GetCacheEntryQuery,
    SetCacheEntryCommand,
)

router = APIRouter(prefix="/api/v1/cache")


@router.put("/{key}")
async def set_cache(
    body: SetCacheRequest,
    container: ContainerDep,
    key: str = Path(min_length=1, max_length=200),
) -> dict[str, object]:
    """Set cache entry in Redis."""
    if "redis" not in container.enabled_modules:
        raise DisabledModuleError("redis")

    result = await container.command_bus.dispatch(
        SetCacheEntryCommand(key=key, value=body.value, ttl_seconds=body.ttl_seconds)
    )
    return result.model_dump()


@router.get("/{key}")
async def get_cache(
    container: ContainerDep,
    key: str = Path(min_length=1, max_length=200),
) -> dict[str, object]:
    """Get cache entry from Redis."""
    if "redis" not in container.enabled_modules:
        raise DisabledModuleError("redis")

    result = await container.query_bus.dispatch(GetCacheEntryQuery(key=key))
    payload = result.model_dump()
    if not result.entry.found:
        raise NotFoundError(
            f"Cache key '{key}' was not found",
            code="cache_not_found",
            details={"key": key},
        )
    return payload


@router.delete("/{key}")
async def delete_cache(
    container: ContainerDep,
    key: str = Path(min_length=1, max_length=200),
) -> dict[str, object]:
    """Delete cache entry from Redis."""
    if "redis" not in container.enabled_modules:
        raise DisabledModuleError("redis")

    result = await container.command_bus.dispatch(DeleteCacheEntryCommand(key=key))
    return result.model_dump()
