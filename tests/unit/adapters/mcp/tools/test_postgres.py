"""Unit tests for Postgres MCP tools."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from sackmesser.adapters.mcp.errors import MCPToolError
from sackmesser.adapters.mcp.tools.postgres import (
    create_workflow_tool,
    get_tool_specs,
    list_workflows_tool,
)
from sackmesser.application.requests.workflows import (
    CreateWorkflowCommand,
    CreateWorkflowResult,
    ListWorkflowsQuery,
    ListWorkflowsResult,
    WorkflowDto,
)


class _FakeCommandBus:
    def __init__(self) -> None:
        self.calls: list[Any] = []

    async def dispatch(self, command: CreateWorkflowCommand) -> CreateWorkflowResult:
        self.calls.append(command)
        return CreateWorkflowResult(
            workflow=WorkflowDto(
                id="wf-1",
                title=command.title,
                payload=command.payload,
                created_at=datetime(2026, 1, 1, tzinfo=UTC),
            )
        )


class _FakeQueryBus:
    def __init__(self) -> None:
        self.calls: list[Any] = []

    async def dispatch(self, query: ListWorkflowsQuery) -> ListWorkflowsResult:
        self.calls.append(query)
        return ListWorkflowsResult(
            workflows=[
                WorkflowDto(
                    id="wf-1",
                    title="demo",
                    payload={},
                    created_at=datetime(2026, 1, 1, tzinfo=UTC),
                )
            ]
        )


class _Container:
    def __init__(self, enabled_modules: set[str]) -> None:
        self.enabled_modules = enabled_modules
        self.command_bus = _FakeCommandBus()
        self.query_bus = _FakeQueryBus()


async def test_create_workflow_tool_dispatches_command() -> None:
    container = _Container(enabled_modules={"core", "postgres"})

    result = await create_workflow_tool(container, {"title": "demo"})

    assert result["workflow"]["title"] == "demo"
    command = container.command_bus.calls[0]
    assert isinstance(command, CreateWorkflowCommand)
    assert command.title == "demo"
    assert command.payload == {}


async def test_create_workflow_tool_raises_module_disabled() -> None:
    container = _Container(enabled_modules={"core"})

    with pytest.raises(MCPToolError) as exc_info:
        await create_workflow_tool(container, {"title": "demo"})

    assert exc_info.value.code == "module_disabled"


async def test_list_workflows_tool_dispatches_query_with_defaults() -> None:
    container = _Container(enabled_modules={"core", "postgres"})

    result = await list_workflows_tool(container, {})

    assert len(result["workflows"]) == 1
    query = container.query_bus.calls[0]
    assert isinstance(query, ListWorkflowsQuery)
    assert query.limit == 20
    assert query.offset == 0


async def test_list_workflows_tool_raises_module_disabled() -> None:
    container = _Container(enabled_modules={"core"})

    with pytest.raises(MCPToolError) as exc_info:
        await list_workflows_tool(container, {"limit": 5, "offset": 1})

    assert exc_info.value.code == "module_disabled"


def test_get_tool_specs_for_postgres_tools() -> None:
    specs = get_tool_specs()

    assert [spec.name for spec in specs] == ["create_workflow", "list_workflows"]
    assert specs[0].handler is create_workflow_tool
    assert specs[1].handler is list_workflows_tool
