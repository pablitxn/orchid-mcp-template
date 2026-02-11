"""Unit tests for MCP error payloads."""

from __future__ import annotations

import pytest

from sackmesser.adapters.mcp.errors import MCPToolError
from sackmesser.adapters.mcp.server import _unknown_tool_payload
from sackmesser.adapters.mcp.tools.redis import cache_get_tool


class _ContainerWithoutRedis:
    enabled_modules = frozenset({"core"})


def test_mcp_tool_error_to_payload() -> None:
    exc = MCPToolError(
        code="module_disabled",
        message="Module 'redis' is disabled",
        details={"module": "redis"},
    )
    payload = exc.to_payload()
    assert payload["error"]["code"] == "module_disabled"
    assert payload["error"]["details"]["module"] == "redis"


def test_unknown_tool_payload_shape() -> None:
    payload = _unknown_tool_payload("demo_tool")
    assert payload["error"]["code"] == "unknown_tool"
    assert payload["error"]["message"] == "Unknown tool: demo_tool"
    assert payload["error"]["details"]["tool"] == "demo_tool"


@pytest.mark.asyncio
async def test_redis_tool_raises_module_disabled_error() -> None:
    with pytest.raises(MCPToolError) as exc_info:
        await cache_get_tool(_ContainerWithoutRedis(), {"key": "demo"})

    assert exc_info.value.code == "module_disabled"
