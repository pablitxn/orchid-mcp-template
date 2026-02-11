"""Core query handlers."""

from __future__ import annotations

from sackmesser.application.requests.core import (
    CapabilityDto,
    GetCapabilitiesQuery,
    GetCapabilitiesResult,
    GetHealthQuery,
    GetHealthResult,
)
from sackmesser.domain.ports.core_ports import CapabilityPort, HealthPort


class GetCapabilitiesQueryHandler:
    """Handle capability listing queries."""

    def __init__(self, capability_port: CapabilityPort) -> None:
        self._capability_port = capability_port

    async def handle(self, _: GetCapabilitiesQuery) -> GetCapabilitiesResult:
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


class GetHealthQueryHandler:
    """Handle health queries."""

    def __init__(self, health_port: HealthPort) -> None:
        self._health_port = health_port

    async def handle(self, _: GetHealthQuery) -> GetHealthResult:
        snapshot = await self._health_port.get_health()
        return GetHealthResult(status=snapshot.status, payload=snapshot.payload)
