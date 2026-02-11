"""Workflow command/query handlers."""

from __future__ import annotations

from sackmesser.application.requests.workflows import (
    CreateWorkflowCommand,
    CreateWorkflowResult,
    ListWorkflowsQuery,
    ListWorkflowsResult,
)
from sackmesser.application.use_cases.workflows import (
    CreateWorkflowUseCase,
    ListWorkflowsUseCase,
)
from sackmesser.domain.ports.workflow_ports import WorkflowRepositoryPort


class CreateWorkflowCommandHandler:
    """Thin adapter for workflow creation use case."""

    def __init__(
        self,
        repository: WorkflowRepositoryPort | None = None,
        *,
        use_case: CreateWorkflowUseCase | None = None,
    ) -> None:
        if use_case is None:
            if repository is None:
                msg = "repository is required when use_case is not provided"
                raise ValueError(msg)
            use_case = CreateWorkflowUseCase(repository)
        self._use_case = use_case

    async def handle(self, command: CreateWorkflowCommand) -> CreateWorkflowResult:
        return await self._use_case.execute(command)


class ListWorkflowsQueryHandler:
    """Thin adapter for workflow listing use case."""

    def __init__(
        self,
        repository: WorkflowRepositoryPort | None = None,
        *,
        use_case: ListWorkflowsUseCase | None = None,
    ) -> None:
        if use_case is None:
            if repository is None:
                msg = "repository is required when use_case is not provided"
                raise ValueError(msg)
            use_case = ListWorkflowsUseCase(repository)
        self._use_case = use_case

    async def handle(self, query: ListWorkflowsQuery) -> ListWorkflowsResult:
        return await self._use_case.execute(query)
