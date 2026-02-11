"""Core use cases."""

from __future__ import annotations

from sackmesser.application.core.dtos import (
    CapabilityDto,
    GetCapabilitiesResult,
    GetHealthResult,
)
from sackmesser.application.core.queries import GetCapabilitiesQuery, GetHealthQuery
from sackmesser.domain.ports.core_ports import CapabilityPort, HealthPort


class GetCapabilitiesUseCase:
    """Return capabilities exposed by runtime configuration."""

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


class GetHealthUseCase:
    """Return normalized health information."""

    def __init__(self, health_port: HealthPort) -> None:
        self._health_port = health_port

    async def execute(self, _: GetHealthQuery) -> GetHealthResult:
        snapshot = await self._health_port.get_health()
        return GetHealthResult(status=snapshot.status, payload=snapshot.payload)
