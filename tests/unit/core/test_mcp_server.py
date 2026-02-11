"""Unit tests for MCP server adapter."""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest
from mcp.types import CallToolRequest, CallToolRequestParams, ListToolsRequest

from sackmesser.adapters.mcp.errors import MCPToolError
from sackmesser.adapters.mcp.server import create_mcp_server, run_mcp_server
from sackmesser.adapters.mcp.tools.common import ToolSpec


@pytest.mark.asyncio
async def test_create_mcp_server_exposes_and_executes_tools(monkeypatch) -> None:
    container = object()
    seen_containers: list[object] = []

    async def ok_tool(handler_container: object, arguments: dict[str, Any]) -> dict[str, Any]:
        seen_containers.append(handler_container)
        return {"ok": True, "arguments": arguments}

    async def controlled_error_tool(_: object, __: dict[str, Any]) -> dict[str, Any]:
        raise MCPToolError(
            code="module_disabled",
            message="Module disabled",
            details={"module": "postgres"},
        )

    async def exploding_tool(_: object, __: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "sackmesser.adapters.mcp.server.get_runtime_state",
        lambda: SimpleNamespace(
            enabled_modules={"core", "postgres"},
            settings=SimpleNamespace(service=SimpleNamespace(name="demo-mcp")),
        ),
    )
    monkeypatch.setattr("sackmesser.adapters.mcp.server.get_runtime_container", lambda: container)
    monkeypatch.setattr(
        "sackmesser.adapters.mcp.server.load_tool_specs",
        lambda _: [
            ToolSpec(
                name="ok_tool",
                description="ok",
                input_schema={},
                handler=ok_tool,
            ),
            ToolSpec(
                name="controlled_error_tool",
                description="err",
                input_schema={},
                handler=controlled_error_tool,
            ),
            ToolSpec(
                name="exploding_tool",
                description="boom",
                input_schema={},
                handler=exploding_tool,
            ),
        ],
    )

    server = create_mcp_server()
    list_handler = server.request_handlers[ListToolsRequest]
    call_handler = server.request_handlers[CallToolRequest]

    listed = await list_handler(ListToolsRequest())
    assert [tool.name for tool in listed.root.tools] == [
        "ok_tool",
        "controlled_error_tool",
        "exploding_tool",
    ]

    ok_response = await call_handler(
        CallToolRequest(params=CallToolRequestParams(name="ok_tool", arguments={"x": 1}))
    )
    ok_payload = json.loads(ok_response.root.content[0].text)
    assert ok_payload == {"ok": True, "arguments": {"x": 1}}
    assert seen_containers == [container]

    known_error_response = await call_handler(
        CallToolRequest(
            params=CallToolRequestParams(name="controlled_error_tool", arguments={})
        )
    )
    known_error_payload = json.loads(known_error_response.root.content[0].text)
    assert known_error_payload["error"]["code"] == "module_disabled"

    unknown_response = await call_handler(
        CallToolRequest(params=CallToolRequestParams(name="missing_tool", arguments={}))
    )
    unknown_payload = json.loads(unknown_response.root.content[0].text)
    assert unknown_payload["error"]["code"] == "unknown_tool"

    crash_response = await call_handler(
        CallToolRequest(params=CallToolRequestParams(name="exploding_tool", arguments={}))
    )
    crash_payload = json.loads(crash_response.root.content[0].text)
    assert crash_payload["error"]["code"] == "internal_error"
    assert crash_payload["error"]["details"]["exception_type"] == "RuntimeError"


@pytest.mark.asyncio
async def test_run_mcp_server_runs_lifecycle(monkeypatch) -> None:
    events: list[object] = []

    async def fake_startup() -> None:
        events.append("startup")

    async def fake_shutdown() -> None:
        events.append("shutdown")

    class _FakeServer:
        def create_initialization_options(self) -> dict[str, str]:
            return {"mode": "test"}

        async def run(
            self,
            read_stream: str,
            write_stream: str,
            options: dict[str, str],
        ) -> None:
            events.append(("run", read_stream, write_stream, options))

    class _FakeStdioContext:
        async def __aenter__(self) -> tuple[str, str]:
            events.append("enter_stdio")
            return ("read_stream", "write_stream")

        async def __aexit__(
            self,
            _exc_type: type[BaseException] | None,
            _exc: BaseException | None,
            _tb: object,
        ) -> bool:
            events.append("exit_stdio")
            return False

    monkeypatch.setattr("sackmesser.adapters.mcp.server.startup_runtime", fake_startup)
    monkeypatch.setattr("sackmesser.adapters.mcp.server.shutdown_runtime", fake_shutdown)
    monkeypatch.setattr(
        "sackmesser.adapters.mcp.server.create_mcp_server",
        lambda: _FakeServer(),
    )
    monkeypatch.setattr(
        "sackmesser.adapters.mcp.server.stdio_server",
        lambda: _FakeStdioContext(),
    )

    await run_mcp_server()

    assert events == [
        "startup",
        "enter_stdio",
        ("run", "read_stream", "write_stream", {"mode": "test"}),
        "exit_stdio",
        "shutdown",
    ]


@pytest.mark.asyncio
async def test_run_mcp_server_shutdowns_even_on_failure(monkeypatch) -> None:
    events: list[str] = []

    async def fake_startup() -> None:
        events.append("startup")

    async def fake_shutdown() -> None:
        events.append("shutdown")

    class _FailingServer:
        def create_initialization_options(self) -> dict[str, str]:
            return {"mode": "test"}

        async def run(self, _: str, __: str, ___: dict[str, str]) -> None:
            raise RuntimeError("boom")

    class _FakeStdioContext:
        async def __aenter__(self) -> tuple[str, str]:
            return ("read_stream", "write_stream")

        async def __aexit__(
            self,
            _exc_type: type[BaseException] | None,
            _exc: BaseException | None,
            _tb: object,
        ) -> bool:
            return False

    monkeypatch.setattr("sackmesser.adapters.mcp.server.startup_runtime", fake_startup)
    monkeypatch.setattr("sackmesser.adapters.mcp.server.shutdown_runtime", fake_shutdown)
    monkeypatch.setattr(
        "sackmesser.adapters.mcp.server.create_mcp_server",
        lambda: _FailingServer(),
    )
    monkeypatch.setattr(
        "sackmesser.adapters.mcp.server.stdio_server",
        lambda: _FakeStdioContext(),
    )

    with pytest.raises(RuntimeError, match="boom"):
        await run_mcp_server()

    assert events == ["startup", "shutdown"]
