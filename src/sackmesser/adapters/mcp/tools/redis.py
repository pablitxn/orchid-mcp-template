"""Redis MCP tools."""

from __future__ import annotations

from typing import Any

from sackmesser.application.redis import (
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
    handler = container.set_cache_entry_handler
    if handler is None:
        return {"error": "Redis module is disabled"}

    command = SetCacheEntryCommand(
        key=arguments["key"],
        value=arguments["value"],
        ttl_seconds=arguments.get("ttl_seconds"),
    )
    return (await handler.handle(command)).model_dump()


async def cache_get_tool(
    container: ApplicationContainer,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Get cache entry in Redis."""
    handler = container.get_cache_entry_handler
    if handler is None:
        return {"error": "Redis module is disabled"}

    query = GetCacheEntryQuery(key=arguments["key"])
    return (await handler.handle(query)).model_dump()


async def cache_delete_tool(
    container: ApplicationContainer,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Delete cache entry in Redis."""
    handler = container.delete_cache_entry_handler
    if handler is None:
        return {"error": "Redis module is disabled"}

    command = DeleteCacheEntryCommand(key=arguments["key"])
    return (await handler.handle(command)).model_dump()


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
