"""Postgres use cases."""

from sackmesser.application.postgres.commands import CreateWorkflowCommand
from sackmesser.application.postgres.dtos import (
    CreateWorkflowResult,
    ListWorkflowsResult,
    WorkflowDto,
)
from sackmesser.application.postgres.queries import ListWorkflowsQuery
from sackmesser.domain.ports.postgres_ports import WorkflowRepositoryPort


class CreateWorkflowUseCase:
    """Create workflow aggregate in repository."""

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


class ListWorkflowsUseCase:
    """List workflow aggregates from repository."""

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
