"""Cache command/query handlers."""

from sackmesser.application.requests.cache import (
    CacheEntryDto,
    DeleteCacheEntryCommand,
    DeleteCacheEntryResult,
    GetCacheEntryQuery,
    GetCacheEntryResult,
    SetCacheEntryCommand,
    SetCacheEntryResult,
)
from sackmesser.domain.ports.cache_ports import CacheRepositoryPort


class SetCacheEntryCommandHandler:
    """Handle cache set commands."""

    def __init__(self, repository: CacheRepositoryPort) -> None:
        self._repository = repository

    async def handle(self, command: SetCacheEntryCommand) -> SetCacheEntryResult:
        success = await self._repository.set(command.key, command.value, command.ttl_seconds)
        return SetCacheEntryResult(success=success, key=command.key)


class GetCacheEntryQueryHandler:
    """Handle cache get queries."""

    def __init__(self, repository: CacheRepositoryPort) -> None:
        self._repository = repository

    async def handle(self, query: GetCacheEntryQuery) -> GetCacheEntryResult:
        cache_entry = await self._repository.get(query.key)
        return GetCacheEntryResult(
            entry=CacheEntryDto(
                key=cache_entry.key,
                value=cache_entry.value,
                found=cache_entry.value is not None,
            )
        )


class DeleteCacheEntryCommandHandler:
    """Handle cache delete commands."""

    def __init__(self, repository: CacheRepositoryPort) -> None:
        self._repository = repository

    async def handle(self, command: DeleteCacheEntryCommand) -> DeleteCacheEntryResult:
        success = await self._repository.delete(command.key)
        return DeleteCacheEntryResult(success=success, key=command.key)
