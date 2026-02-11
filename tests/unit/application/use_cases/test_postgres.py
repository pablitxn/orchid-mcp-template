"""Unit tests for workflow request handlers."""

from __future__ import annotations

from datetime import UTC, datetime

from sackmesser.application.handlers.workflows import (
    CreateWorkflowCommandHandler,
    ListWorkflowsQueryHandler,
)
from sackmesser.application.requests.workflows import (
    CreateWorkflowCommand,
    ListWorkflowsQuery,
)
from sackmesser.domain.workflows import Workflow


class _FakeWorkflowRepository:
    def __init__(self) -> None:
        self._items: list[Workflow] = []

    async def create(self, title: str, payload: dict[str, object]) -> Workflow:
        workflow = Workflow(
            id=f"wf-{len(self._items)+1}",
            title=title,
            payload=dict(payload),
            created_at=datetime.now(tz=UTC),
        )
        self._items.append(workflow)
        return workflow

    async def list(self, *, limit: int, offset: int) -> list[Workflow]:
        return self._items[offset : offset + limit]


async def test_create_workflow_command_handler() -> None:
    repository = _FakeWorkflowRepository()
    handler = CreateWorkflowCommandHandler(repository)

    result = await handler.handle(
        CreateWorkflowCommand(title="demo", payload={"kind": "smoke"})
    )
    assert result.workflow.title == "demo"
    assert result.workflow.payload["kind"] == "smoke"


async def test_list_workflows_query_handler() -> None:
    repository = _FakeWorkflowRepository()
    await repository.create("one", {})
    await repository.create("two", {})

    handler = ListWorkflowsQueryHandler(repository)
    result = await handler.handle(ListWorkflowsQuery(limit=10, offset=0))
    assert len(result.workflows) == 2
