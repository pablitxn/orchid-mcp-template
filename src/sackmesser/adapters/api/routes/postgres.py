"""Postgres workflow API routes."""

from __future__ import annotations

from fastapi import APIRouter, Query, status

from sackmesser.adapters.dependencies import ContainerDep
from sackmesser.adapters.api.schemas import CreateWorkflowRequest
from sackmesser.application.errors import DisabledModuleError
from sackmesser.application.postgres import CreateWorkflowCommand, ListWorkflowsQuery

router = APIRouter(prefix="/api/v1/workflows")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workflow(
    body: CreateWorkflowRequest,
    container: ContainerDep,
) -> dict[str, object]:
    """Create a workflow in Postgres."""
    handler = container.create_workflow_handler
    if handler is None:
        raise DisabledModuleError("postgres")

    result = await handler.handle(
        CreateWorkflowCommand(title=body.title, payload=body.payload)
    )
    return result.model_dump()


@router.get("")
async def list_workflows(
    container: ContainerDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, object]:
    """List workflows from Postgres."""
    handler = container.list_workflows_handler
    if handler is None:
        raise DisabledModuleError("postgres")

    result = await handler.handle(ListWorkflowsQuery(limit=limit, offset=offset))
    return result.model_dump()
