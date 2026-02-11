"""Unit tests for Redis MCP tools."""

from __future__ import annotations

from typing import Any

import pytest

from sackmesser.adapters.mcp.errors import MCPToolError
from sackmesser.adapters.mcp.tools.redis import (
    cache_delete_tool,
    cache_get_tool,
    cache_set_tool,
    get_tool_specs,
)
from sackmesser.application.requests.cache import (
    CacheEntryDto,
    DeleteCacheEntryCommand,
    DeleteCacheEntryResult,
    GetCacheEntryQuery,
    GetCacheEntryResult,
    SetCacheEntryCommand,
    SetCacheEntryResult,
)


class _FakeCommandBus:
    def __init__(self) -> None:
        self.calls: list[Any] = []

    async def dispatch(
        self,
        command: SetCacheEntryCommand | DeleteCacheEntryCommand,
    ) -> SetCacheEntryResult | DeleteCacheEntryResult:
        self.calls.append(command)
        if isinstance(command, SetCacheEntryCommand):
            return SetCacheEntryResult(success=True, key=command.key)
        if isinstance(command, DeleteCacheEntryCommand):
            return DeleteCacheEntryResult(success=True, key=command.key)
        msg = f"Unexpected command: {type(command)!r}"
        raise AssertionError(msg)


class _FakeQueryBus:
    def __init__(self, *, found: bool, value: str | None = "demo") -> None:
        self.found = found
        self.value = value
        self.calls: list[Any] = []

    async def dispatch(self, query: GetCacheEntryQuery) -> GetCacheEntryResult:
        self.calls.append(query)
        return GetCacheEntryResult(
            entry=CacheEntryDto(
                key=query.key,
                value=self.value if self.found else None,
                found=self.found,
            )
        )


class _Container:
    def __init__(self, enabled_modules: set[str], *, found: bool = True) -> None:
        self.enabled_modules = enabled_modules
        self.command_bus = _FakeCommandBus()
        self.query_bus = _FakeQueryBus(found=found)


async def test_cache_set_tool_dispatches_command() -> None:
    container = _Container(enabled_modules={"core", "redis"})

    result = await cache_set_tool(
        container,
        {"key": "alpha", "value": "1", "ttl_seconds": 10},
    )

    assert result == {"success": True, "key": "alpha"}
    command = container.command_bus.calls[0]
    assert isinstance(command, SetCacheEntryCommand)
    assert command.key == "alpha"
    assert command.value == "1"
    assert command.ttl_seconds == 10


async def test_cache_set_tool_raises_module_disabled() -> None:
    container = _Container(enabled_modules={"core"})

    with pytest.raises(MCPToolError) as exc_info:
        await cache_set_tool(container, {"key": "alpha", "value": "1"})

    assert exc_info.value.code == "module_disabled"


async def test_cache_get_tool_returns_entry_payload() -> None:
    container = _Container(enabled_modules={"core", "redis"}, found=True)

    result = await cache_get_tool(container, {"key": "alpha"})

    assert result["entry"]["found"] is True
    assert result["entry"]["value"] == "demo"
    query = container.query_bus.calls[0]
    assert isinstance(query, GetCacheEntryQuery)


async def test_cache_get_tool_raises_cache_not_found() -> None:
    container = _Container(enabled_modules={"core", "redis"}, found=False)

    with pytest.raises(MCPToolError) as exc_info:
        await cache_get_tool(container, {"key": "missing"})

    assert exc_info.value.code == "cache_not_found"
    assert exc_info.value.details["key"] == "missing"


async def test_cache_delete_tool_dispatches_command() -> None:
    container = _Container(enabled_modules={"core", "redis"})

    result = await cache_delete_tool(container, {"key": "alpha"})

    assert result == {"success": True, "key": "alpha"}
    command = container.command_bus.calls[0]
    assert isinstance(command, DeleteCacheEntryCommand)
    assert command.key == "alpha"


async def test_cache_delete_tool_raises_module_disabled() -> None:
    container = _Container(enabled_modules={"core"})

    with pytest.raises(MCPToolError) as exc_info:
        await cache_delete_tool(container, {"key": "alpha"})

    assert exc_info.value.code == "module_disabled"


def test_get_tool_specs_for_redis_tools() -> None:
    specs = get_tool_specs()

    assert [spec.name for spec in specs] == ["cache_set", "cache_get", "cache_delete"]
    assert specs[0].handler is cache_set_tool
    assert specs[1].handler is cache_get_tool
    assert specs[2].handler is cache_delete_tool
