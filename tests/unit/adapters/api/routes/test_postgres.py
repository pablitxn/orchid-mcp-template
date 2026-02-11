"""Unit tests for Postgres API routes."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from sackmesser.adapters.api.routes.postgres import create_workflow, list_workflows
from sackmesser.adapters.api.schemas import CreateWorkflowRequest
from sackmesser.application.errors import DisabledModuleError
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


async def test_create_workflow_route_dispatches_command() -> None:
    container = _Container(enabled_modules={"core", "postgres"})
    body = CreateWorkflowRequest(title="demo", payload={"k": "v"})

    payload = await create_workflow(body, container)

    assert payload["workflow"]["title"] == "demo"
    command = container.command_bus.calls[0]
    assert isinstance(command, CreateWorkflowCommand)
    assert command.payload == {"k": "v"}


async def test_create_workflow_route_raises_if_module_disabled() -> None:
    container = _Container(enabled_modules={"core"})
    body = CreateWorkflowRequest(title="demo")

    with pytest.raises(DisabledModuleError) as exc_info:
        await create_workflow(body, container)

    assert exc_info.value.code == "module_disabled"


async def test_list_workflows_route_dispatches_query() -> None:
    container = _Container(enabled_modules={"core", "postgres"})

    payload = await list_workflows(container, limit=5, offset=2)

    assert len(payload["workflows"]) == 1
    query = container.query_bus.calls[0]
    assert isinstance(query, ListWorkflowsQuery)
    assert query.limit == 5
    assert query.offset == 2


async def test_list_workflows_route_raises_if_module_disabled() -> None:
    container = _Container(enabled_modules={"core"})

    with pytest.raises(DisabledModuleError) as exc_info:
        await list_workflows(container, limit=5, offset=0)

    assert exc_info.value.code == "module_disabled"
