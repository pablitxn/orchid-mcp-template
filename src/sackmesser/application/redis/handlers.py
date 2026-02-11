"""Redis handlers."""

from sackmesser.application.redis.commands import (
    DeleteCacheEntryCommand,
    SetCacheEntryCommand,
)
from sackmesser.application.redis.dtos import (
    DeleteCacheEntryResult,
    GetCacheEntryResult,
    SetCacheEntryResult,
)
from sackmesser.application.redis.queries import GetCacheEntryQuery
from sackmesser.application.redis.use_cases import (
    DeleteCacheEntryUseCase,
    GetCacheEntryUseCase,
    SetCacheEntryUseCase,
)


class SetCacheEntryHandler:
    """Handle cache set command."""

    def __init__(self, use_case: SetCacheEntryUseCase) -> None:
        self._use_case = use_case

    async def handle(self, command: SetCacheEntryCommand) -> SetCacheEntryResult:
        return await self._use_case.execute(command)


class GetCacheEntryHandler:
    """Handle cache get query."""

    def __init__(self, use_case: GetCacheEntryUseCase) -> None:
        self._use_case = use_case

    async def handle(self, query: GetCacheEntryQuery) -> GetCacheEntryResult:
        return await self._use_case.execute(query)


class DeleteCacheEntryHandler:
    """Handle cache delete command."""

    def __init__(self, use_case: DeleteCacheEntryUseCase) -> None:
        self._use_case = use_case

    async def handle(self, command: DeleteCacheEntryCommand) -> DeleteCacheEntryResult:
        return await self._use_case.execute(command)
