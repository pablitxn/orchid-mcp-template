"""Cache command/query use cases."""

from sackmesser.application.requests.cache import (
    CacheEntryDto,
    DeleteCacheEntryCommand,
    DeleteCacheEntryResult,
    GetCacheEntryQuery,
    GetCacheEntryResult,
    SetCacheEntryCommand,
    SetCacheEntryResult,
)
from sackmesser.application.use_cases.base import BaseUseCase
from sackmesser.domain.ports.cache_ports import CacheRepositoryPort


class SetCacheEntryUseCase(BaseUseCase[SetCacheEntryCommand, SetCacheEntryResult]):
    """Write values into cache storage."""

    def __init__(self, repository: CacheRepositoryPort) -> None:
        self._repository = repository

    async def execute(self, command: SetCacheEntryCommand) -> SetCacheEntryResult:
        success = await self._repository.set(command.key, command.value, command.ttl_seconds)
        return SetCacheEntryResult(success=success, key=command.key)


class GetCacheEntryUseCase(BaseUseCase[GetCacheEntryQuery, GetCacheEntryResult]):
    """Fetch values from cache storage."""

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


class DeleteCacheEntryUseCase(BaseUseCase[DeleteCacheEntryCommand, DeleteCacheEntryResult]):
    """Delete values from cache storage."""

    def __init__(self, repository: CacheRepositoryPort) -> None:
        self._repository = repository

    async def execute(self, command: DeleteCacheEntryCommand) -> DeleteCacheEntryResult:
        success = await self._repository.delete(command.key)
        return DeleteCacheEntryResult(success=success, key=command.key)
