"""Core query use cases."""

from __future__ import annotations

from sackmesser.application.requests.core import (
    CapabilityDto,
    GetCapabilitiesQuery,
    GetCapabilitiesResult,
    GetHealthQuery,
    GetHealthResult,
)
from sackmesser.application.use_cases.base import BaseUseCase
from sackmesser.domain.ports.core_ports import CapabilityPort, HealthPort


class GetCapabilitiesUseCase(BaseUseCase[GetCapabilitiesQuery, GetCapabilitiesResult]):
    """Return available capabilities for active modules/resources."""

    def __init__(self, capability_port: CapabilityPort) -> None:
        self._capability_port = capability_port

    async def execute(self, _: GetCapabilitiesQuery) -> GetCapabilitiesResult:
        capabilities = await self._capability_port.list_capabilities()
        return GetCapabilitiesResult(
            capabilities=[
                CapabilityDto(
                    name=item.name,
                    enabled=item.enabled,
                    description=item.description,
                    resources=list(item.resources),
                )
                for item in capabilities
            ]
        )


class GetHealthUseCase(BaseUseCase[GetHealthQuery, GetHealthResult]):
    """Return runtime health snapshot."""

    def __init__(self, health_port: HealthPort) -> None:
        self._health_port = health_port

    async def execute(self, _: GetHealthQuery) -> GetHealthResult:
        snapshot = await self._health_port.get_health()
        return GetHealthResult(status=snapshot.status, payload=snapshot.payload)
