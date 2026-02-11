"""Cache command/query handlers."""

from sackmesser.application.requests.cache import (
    DeleteCacheEntryCommand,
    DeleteCacheEntryResult,
    GetCacheEntryQuery,
    GetCacheEntryResult,
    SetCacheEntryCommand,
    SetCacheEntryResult,
)
from sackmesser.application.use_cases.cache import (
    DeleteCacheEntryUseCase,
    GetCacheEntryUseCase,
    SetCacheEntryUseCase,
)
from sackmesser.domain.ports.cache_ports import CacheRepositoryPort


class SetCacheEntryCommandHandler:
    """Thin adapter for cache set use case."""

    def __init__(
        self,
        repository: CacheRepositoryPort | None = None,
        *,
        use_case: SetCacheEntryUseCase | None = None,
    ) -> None:
        if use_case is None:
            if repository is None:
                msg = "repository is required when use_case is not provided"
                raise ValueError(msg)
            use_case = SetCacheEntryUseCase(repository)
        self._use_case = use_case

    async def handle(self, command: SetCacheEntryCommand) -> SetCacheEntryResult:
        return await self._use_case.execute(command)


class GetCacheEntryQueryHandler:
    """Thin adapter for cache get use case."""

    def __init__(
        self,
        repository: CacheRepositoryPort | None = None,
        *,
        use_case: GetCacheEntryUseCase | None = None,
    ) -> None:
        if use_case is None:
            if repository is None:
                msg = "repository is required when use_case is not provided"
                raise ValueError(msg)
            use_case = GetCacheEntryUseCase(repository)
        self._use_case = use_case

    async def handle(self, query: GetCacheEntryQuery) -> GetCacheEntryResult:
        return await self._use_case.execute(query)


class DeleteCacheEntryCommandHandler:
    """Thin adapter for cache delete use case."""

    def __init__(
        self,
        repository: CacheRepositoryPort | None = None,
        *,
        use_case: DeleteCacheEntryUseCase | None = None,
    ) -> None:
        if use_case is None:
            if repository is None:
                msg = "repository is required when use_case is not provided"
                raise ValueError(msg)
            use_case = DeleteCacheEntryUseCase(repository)
        self._use_case = use_case

    async def handle(self, command: DeleteCacheEntryCommand) -> DeleteCacheEntryResult:
        return await self._use_case.execute(command)
