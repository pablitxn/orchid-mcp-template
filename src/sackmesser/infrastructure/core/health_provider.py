"""Health adapter backed by commons ResourceManager."""

from __future__ import annotations

from orchid_commons import ResourceManager

from sackmesser.domain.core.models import HealthSnapshot
from sackmesser.domain.ports.core_ports import HealthPort


class ResourceManagerHealthProvider(HealthPort):
    """Adapts ResourceManager health payload to domain model."""

    def __init__(self, manager: ResourceManager) -> None:
        self._manager = manager

    async def get_health(self) -> HealthSnapshot:
        payload = await self._manager.health_payload()
        status = str(payload.get("status", "unknown"))
        return HealthSnapshot(status=status, payload=payload)
