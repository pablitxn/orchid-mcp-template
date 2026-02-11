"""Core MCP tools."""

from __future__ import annotations

from sackmesser.application.requests.core import GetCapabilitiesQuery, GetHealthQuery
from sackmesser.infrastructure.runtime.container import ApplicationContainer

from .common import ToolSpec


async def health_check_tool(
    container: ApplicationContainer,
    _arguments: dict[str, object],
) -> dict[str, object]:
    """Return health report from ResourceManager."""
    result = await container.query_bus.dispatch(GetHealthQuery())
    return result.payload


async def list_capabilities_tool(
    container: ApplicationContainer,
    _arguments: dict[str, object],
) -> dict[str, object]:
    """Return enabled capabilities."""
    result = await container.query_bus.dispatch(GetCapabilitiesQuery())
    return result.model_dump()


def get_tool_specs() -> list[ToolSpec]:
    """Return MCP tool specs for core module."""
    return [
        ToolSpec(
            name="health_check",
            description="Get aggregated health of all active resources.",
            input_schema={"type": "object", "properties": {}},
            handler=health_check_tool,
        ),
        ToolSpec(
            name="list_capabilities",
            description="List template capabilities and their enabled status.",
            input_schema={"type": "object", "properties": {}},
            handler=list_capabilities_tool,
        ),
    ]
