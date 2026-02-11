"""Core handlers (thin wrappers over use cases)."""

from sackmesser.application.core.dtos import GetCapabilitiesResult, GetHealthResult
from sackmesser.application.core.queries import GetCapabilitiesQuery, GetHealthQuery
from sackmesser.application.core.use_cases import GetCapabilitiesUseCase, GetHealthUseCase


class GetCapabilitiesHandler:
    """Handle capability listing requests."""

    def __init__(self, use_case: GetCapabilitiesUseCase) -> None:
        self._use_case = use_case

    async def handle(self, query: GetCapabilitiesQuery) -> GetCapabilitiesResult:
        return await self._use_case.execute(query)


class GetHealthHandler:
    """Handle health requests."""

    def __init__(self, use_case: GetHealthUseCase) -> None:
        self._use_case = use_case

    async def handle(self, query: GetHealthQuery) -> GetHealthResult:
        return await self._use_case.execute(query)
