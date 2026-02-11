"""MCP server with dynamic tool registration per enabled module."""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool

from sackmesser.adapters.mcp.tools import load_tool_specs
from sackmesser.infrastructure.runtime import (
    get_runtime_container,
    get_runtime_state,
    shutdown_runtime,
    startup_runtime,
)


def create_mcp_server() -> Server:
    """Create MCP server using runtime enabled modules."""
    state = get_runtime_state()
    tool_specs = load_tool_specs(state.enabled_modules)
    tool_map = {spec.name: spec for spec in tool_specs}

    server = Server(state.settings.service.name)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=tool.name,
                description=tool.description,
                inputSchema=tool.input_schema,
            )
            for tool in tool_specs
        ]

    @server.call_tool()
    async def call_tool(
        name: str,
        arguments: dict[str, Any],
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        container = get_runtime_container()
        tool = tool_map.get(name)
        if tool is None:
            payload = {"error": f"Unknown tool: {name}"}
            return [TextContent(type="text", text=json.dumps(payload))]

        try:
            result = await tool.handler(container, arguments)
        except Exception as exc:
            result = {"error": str(exc), "tool": name}

        return [TextContent(type="text", text=json.dumps(result, default=str))]

    return server


async def run_mcp_server() -> None:
    """Run MCP stdio server with runtime lifecycle management."""
    await startup_runtime()
    server = create_mcp_server()

    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
    finally:
        await shutdown_runtime()
