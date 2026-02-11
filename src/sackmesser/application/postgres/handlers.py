"""Postgres handlers."""

from sackmesser.application.postgres.commands import CreateWorkflowCommand
from sackmesser.application.postgres.dtos import CreateWorkflowResult, ListWorkflowsResult
from sackmesser.application.postgres.queries import ListWorkflowsQuery
from sackmesser.application.postgres.use_cases import (
    CreateWorkflowUseCase,
    ListWorkflowsUseCase,
)


class CreateWorkflowHandler:
    """Handle workflow creation commands."""

    def __init__(self, use_case: CreateWorkflowUseCase) -> None:
        self._use_case = use_case

    async def handle(self, command: CreateWorkflowCommand) -> CreateWorkflowResult:
        return await self._use_case.execute(command)


class ListWorkflowsHandler:
    """Handle workflow list queries."""

    def __init__(self, use_case: ListWorkflowsUseCase) -> None:
        self._use_case = use_case

    async def handle(self, query: ListWorkflowsQuery) -> ListWorkflowsResult:
        return await self._use_case.execute(query)
