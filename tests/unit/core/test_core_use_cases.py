"""Unit tests for core request handlers."""

from __future__ import annotations

from sackmesser.application.handlers.core import (
    GetCapabilitiesQueryHandler,
    GetHealthQueryHandler,
)
from sackmesser.application.requests.core import GetCapabilitiesQuery, GetHealthQuery
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


async def test_get_capabilities_handler_returns_items() -> None:
    handler = GetCapabilitiesQueryHandler(_FakeCapabilityPort())
    result = await handler.handle(GetCapabilitiesQuery())
    assert len(result.capabilities) == 2
    assert result.capabilities[0].name == "core"


async def test_get_health_handler_returns_snapshot() -> None:
    handler = GetHealthQueryHandler(_FakeHealthPort())
    result = await handler.handle(GetHealthQuery())
    assert result.status == "ok"
    assert result.payload["status"] == "ok"
