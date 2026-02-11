"""Workflow command/query handlers (application use cases)."""

from __future__ import annotations

from sackmesser.application.workflows.commands import CreateWorkflowCommand
from sackmesser.application.workflows.dtos import (
    CreateWorkflowResult,
    ListWorkflowsResult,
    WorkflowDto,
)
from sackmesser.application.workflows.queries import ListWorkflowsQuery
from sackmesser.domain.ports.workflow_ports import WorkflowRepositoryPort


class CreateWorkflowCommandHandler:
    """Handle workflow creation commands."""

    def __init__(self, repository: WorkflowRepositoryPort) -> None:
        self._repository = repository

    async def handle(self, command: CreateWorkflowCommand) -> CreateWorkflowResult:
        workflow = await self._repository.create(command.title, command.payload)
        return CreateWorkflowResult(
            workflow=WorkflowDto(
                id=workflow.id,
                title=workflow.title,
                payload=workflow.payload,
                created_at=workflow.created_at,
            )
        )


class ListWorkflowsQueryHandler:
    """Handle workflow list queries."""

    def __init__(self, repository: WorkflowRepositoryPort) -> None:
        self._repository = repository

    async def handle(self, query: ListWorkflowsQuery) -> ListWorkflowsResult:
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


# Backward-compatible aliases (older API exported *Handler names without CQRS kind)
CreateWorkflowHandler = CreateWorkflowCommandHandler
ListWorkflowsHandler = ListWorkflowsQueryHandler

# Backward-compatible aliases for previous UseCase naming
CreateWorkflowUseCase = CreateWorkflowCommandHandler
ListWorkflowsUseCase = ListWorkflowsQueryHandler
