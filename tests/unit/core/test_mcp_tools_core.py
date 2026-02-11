"""Unit tests for core MCP tools."""

from __future__ import annotations

from typing import Any

from sackmesser.adapters.mcp.tools.core import (
    get_tool_specs,
    health_check_tool,
    list_capabilities_tool,
)
from sackmesser.application.requests.core import (
    CapabilityDto,
    GetCapabilitiesQuery,
    GetCapabilitiesResult,
    GetHealthQuery,
    GetHealthResult,
)


class _FakeQueryBus:
    def __init__(self) -> None:
        self.calls: list[Any] = []

    async def dispatch(self, request: Any) -> GetHealthResult | GetCapabilitiesResult:
        self.calls.append(request)
        if isinstance(request, GetHealthQuery):
            return GetHealthResult(status="ok", payload={"status": "ok", "checks": {}})
        if isinstance(request, GetCapabilitiesQuery):
            return GetCapabilitiesResult(
                capabilities=[
                    CapabilityDto(
                        name="core",
                        enabled=True,
                        description="Core module",
                        resources=[],
                    )
                ]
            )
        msg = f"Unexpected request: {type(request)!r}"
        raise AssertionError(msg)


class _FakeContainer:
    def __init__(self) -> None:
        self.query_bus = _FakeQueryBus()


async def test_health_check_tool_returns_payload() -> None:
    container = _FakeContainer()

    result = await health_check_tool(container, {})

    assert result == {"status": "ok", "checks": {}}
    assert isinstance(container.query_bus.calls[0], GetHealthQuery)


async def test_list_capabilities_tool_returns_serialized_result() -> None:
    container = _FakeContainer()

    result = await list_capabilities_tool(container, {})

    assert "capabilities" in result
    assert result["capabilities"][0]["name"] == "core"
    assert isinstance(container.query_bus.calls[0], GetCapabilitiesQuery)


def test_get_tool_specs_exposes_core_tools() -> None:
    specs = get_tool_specs()
    names = [item.name for item in specs]

    assert names == ["health_check", "list_capabilities"]
    assert specs[0].handler is health_check_tool
    assert specs[1].handler is list_capabilities_tool
