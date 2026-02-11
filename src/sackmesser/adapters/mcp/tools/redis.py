"""Redis MCP tools."""

from __future__ import annotations

from typing import Any

from sackmesser.adapters.mcp.errors import MCPToolError
from sackmesser.application.requests.cache import (
    DeleteCacheEntryCommand,
    GetCacheEntryQuery,
    SetCacheEntryCommand,
)
from sackmesser.infrastructure.runtime.container import ApplicationContainer

from .common import ToolSpec


async def cache_set_tool(
    container: ApplicationContainer,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Set cache entry in Redis."""
    if "redis" not in container.enabled_modules:
        raise MCPToolError(
            code="module_disabled",
            message="Module 'redis' is disabled",
            details={"module": "redis"},
        )

    command = SetCacheEntryCommand(
        key=arguments["key"],
        value=arguments["value"],
        ttl_seconds=arguments.get("ttl_seconds"),
    )
    return (await container.command_bus.dispatch(command)).model_dump()


async def cache_get_tool(
    container: ApplicationContainer,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Get cache entry in Redis."""
    if "redis" not in container.enabled_modules:
        raise MCPToolError(
            code="module_disabled",
            message="Module 'redis' is disabled",
            details={"module": "redis"},
        )

    query = GetCacheEntryQuery(key=arguments["key"])
    result = await container.query_bus.dispatch(query)
    if not result.entry.found:
        raise MCPToolError(
            code="cache_not_found",
            message=f"Cache key '{arguments['key']}' was not found",
            details={"key": arguments["key"]},
        )
    return result.model_dump()


async def cache_delete_tool(
    container: ApplicationContainer,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Delete cache entry in Redis."""
    if "redis" not in container.enabled_modules:
        raise MCPToolError(
            code="module_disabled",
            message="Module 'redis' is disabled",
            details={"module": "redis"},
        )

    command = DeleteCacheEntryCommand(key=arguments["key"])
    return (await container.command_bus.dispatch(command)).model_dump()


def get_tool_specs() -> list[ToolSpec]:
    """Return MCP tool specs for redis module."""
    return [
        ToolSpec(
            name="cache_set",
            description="Set a cache key in Redis.",
            input_schema={
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "string"},
                    "ttl_seconds": {"type": "integer", "minimum": 1},
                },
                "required": ["key", "value"],
            },
            handler=cache_set_tool,
        ),
        ToolSpec(
            name="cache_get",
            description="Get a cache key from Redis.",
            input_schema={
                "type": "object",
                "properties": {"key": {"type": "string"}},
                "required": ["key"],
            },
            handler=cache_get_tool,
        ),
        ToolSpec(
            name="cache_delete",
            description="Delete a cache key from Redis.",
            input_schema={
                "type": "object",
                "properties": {"key": {"type": "string"}},
                "required": ["key"],
            },
            handler=cache_delete_tool,
        ),
    ]
