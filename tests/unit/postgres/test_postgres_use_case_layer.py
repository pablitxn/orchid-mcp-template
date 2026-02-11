"""Unit tests for workflow use cases."""

from __future__ import annotations

from datetime import UTC, datetime

from sackmesser.application.requests.workflows import CreateWorkflowCommand, ListWorkflowsQuery
from sackmesser.application.use_cases.workflows import (
    CreateWorkflowUseCase,
    ListWorkflowsUseCase,
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


async def test_create_workflow_use_case() -> None:
    repository = _FakeWorkflowRepository()
    use_case = CreateWorkflowUseCase(repository)

    result = await use_case.execute(
        CreateWorkflowCommand(title="demo", payload={"kind": "smoke"})
    )
    assert result.workflow.title == "demo"
    assert result.workflow.payload["kind"] == "smoke"


async def test_list_workflows_use_case() -> None:
    repository = _FakeWorkflowRepository()
    await repository.create("one", {})
    await repository.create("two", {})

    use_case = ListWorkflowsUseCase(repository)
    result = await use_case.execute(ListWorkflowsQuery(limit=10, offset=0))
    assert len(result.workflows) == 2
