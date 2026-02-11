"""Workflow command/query use cases."""

from __future__ import annotations

from sackmesser.application.requests.workflows import (
    CreateWorkflowCommand,
    CreateWorkflowResult,
    ListWorkflowsQuery,
    ListWorkflowsResult,
    WorkflowDto,
)
from sackmesser.application.use_cases.base import BaseUseCase
from sackmesser.domain.ports.workflow_ports import WorkflowRepositoryPort


class CreateWorkflowUseCase(BaseUseCase[CreateWorkflowCommand, CreateWorkflowResult]):
    """Create workflow aggregates."""

    def __init__(self, repository: WorkflowRepositoryPort) -> None:
        self._repository = repository

    async def execute(self, command: CreateWorkflowCommand) -> CreateWorkflowResult:
        workflow = await self._repository.create(command.title, command.payload)
        return CreateWorkflowResult(
            workflow=WorkflowDto(
                id=workflow.id,
                title=workflow.title,
                payload=workflow.payload,
                created_at=workflow.created_at,
            )
        )


class ListWorkflowsUseCase(BaseUseCase[ListWorkflowsQuery, ListWorkflowsResult]):
    """List workflow aggregates."""

    def __init__(self, repository: WorkflowRepositoryPort) -> None:
        self._repository = repository

    async def execute(self, query: ListWorkflowsQuery) -> ListWorkflowsResult:
        workflows = await self._repository.list(limit=query.limit, offset=query.offset)
        return ListWorkflowsResult(
            workflows=[
                WorkflowDto(
                    id=item.id,
                    title=item.title,
                    payload=item.payload,
                    created_at=item.created_at,
                )
                for item in workflows
            ]
        )
