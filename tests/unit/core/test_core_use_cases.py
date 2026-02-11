"""Unit tests for core use cases."""

from __future__ import annotations

from sackmesser.application.core import (
    GetCapabilitiesQuery,
    GetCapabilitiesUseCase,
    GetHealthQuery,
    GetHealthUseCase,
)
from sackmesser.domain.core import Capability, HealthSnapshot


class _FakeCapabilityPort:
    async def list_capabilities(self) -> list[Capability]:
        return [
            Capability(
                name="core",
                enabled=True,
                description="base",
                resources=(),
            ),
            Capability(
                name="postgres",
                enabled=False,
                description="db",
                resources=("postgres",),
            ),
        ]


class _FakeHealthPort:
    async def get_health(self) -> HealthSnapshot:
        return HealthSnapshot(status="ok", payload={"status": "ok", "checks": {}})


async def test_get_capabilities_use_case_returns_items() -> None:
    use_case = GetCapabilitiesUseCase(_FakeCapabilityPort())
    result = await use_case.execute(GetCapabilitiesQuery())
    assert len(result.capabilities) == 2
    assert result.capabilities[0].name == "core"


async def test_get_health_use_case_returns_snapshot() -> None:
    use_case = GetHealthUseCase(_FakeHealthPort())
    result = await use_case.execute(GetHealthQuery())
    assert result.status == "ok"
    assert result.payload["status"] == "ok"
