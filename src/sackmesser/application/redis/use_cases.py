"""Redis use cases."""

from sackmesser.application.redis.commands import (
    DeleteCacheEntryCommand,
    SetCacheEntryCommand,
)
from sackmesser.application.redis.dtos import (
    CacheEntryDto,
    DeleteCacheEntryResult,
    GetCacheEntryResult,
    SetCacheEntryResult,
)
from sackmesser.application.redis.queries import GetCacheEntryQuery
from sackmesser.domain.ports.redis_ports import CacheRepositoryPort


class SetCacheEntryUseCase:
    """Set cache entry through cache port."""

    def __init__(self, repository: CacheRepositoryPort) -> None:
        self._repository = repository

    async def execute(self, command: SetCacheEntryCommand) -> SetCacheEntryResult:
        success = await self._repository.set(command.key, command.value, command.ttl_seconds)
        return SetCacheEntryResult(success=success, key=command.key)


class GetCacheEntryUseCase:
    """Get cache entry through cache port."""

    def __init__(self, repository: CacheRepositoryPort) -> None:
        self._repository = repository

    async def execute(self, query: GetCacheEntryQuery) -> GetCacheEntryResult:
        cache_entry = await self._repository.get(query.key)
        return GetCacheEntryResult(
            entry=CacheEntryDto(
                key=cache_entry.key,
                value=cache_entry.value,
                found=cache_entry.value is not None,
            )
        )


class DeleteCacheEntryUseCase:
    """Delete cache entry through cache port."""

    def __init__(self, repository: CacheRepositoryPort) -> None:
        self._repository = repository

    async def execute(self, command: DeleteCacheEntryCommand) -> DeleteCacheEntryResult:
        success = await self._repository.delete(command.key)
        return DeleteCacheEntryResult(success=success, key=command.key)
