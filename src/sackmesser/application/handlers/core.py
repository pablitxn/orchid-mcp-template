"""Core query handlers."""

from __future__ import annotations

from sackmesser.application.requests.core import (
    GetCapabilitiesQuery,
    GetCapabilitiesResult,
    GetHealthQuery,
    GetHealthResult,
)
from sackmesser.application.use_cases.core import GetCapabilitiesUseCase, GetHealthUseCase
from sackmesser.domain.ports.core_ports import CapabilityPort, HealthPort


class GetCapabilitiesQueryHandler:
    """Thin adapter for capability listing use case."""

    def __init__(
        self,
        capability_port: CapabilityPort | None = None,
        *,
        use_case: GetCapabilitiesUseCase | None = None,
    ) -> None:
        if use_case is None:
            if capability_port is None:
                msg = "capability_port is required when use_case is not provided"
                raise ValueError(msg)
            use_case = GetCapabilitiesUseCase(capability_port)
        self._use_case = use_case

    async def handle(self, query: GetCapabilitiesQuery) -> GetCapabilitiesResult:
        return await self._use_case.execute(query)


class GetHealthQueryHandler:
    """Thin adapter for health query use case."""

    def __init__(
        self,
        health_port: HealthPort | None = None,
        *,
        use_case: GetHealthUseCase | None = None,
    ) -> None:
        if use_case is None:
            if health_port is None:
                msg = "health_port is required when use_case is not provided"
                raise ValueError(msg)
            use_case = GetHealthUseCase(health_port)
        self._use_case = use_case

    async def handle(self, query: GetHealthQuery) -> GetHealthResult:
        return await self._use_case.execute(query)
