"""Postgres workflow API routes."""

from __future__ import annotations

from fastapi import APIRouter, Query, status

from sackmesser.adapters.dependencies import ContainerDep
from sackmesser.adapters.api.schemas import CreateWorkflowRequest
from sackmesser.application.errors import DisabledModuleError
from sackmesser.application.workflows import CreateWorkflowCommand, ListWorkflowsQuery

router = APIRouter(prefix="/api/v1/workflows")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workflow(
    body: CreateWorkflowRequest,
    container: ContainerDep,
) -> dict[str, object]:
    """Create a workflow in Postgres."""
    if "postgres" not in container.enabled_modules:
        raise DisabledModuleError("postgres")

    result = await container.command_bus.dispatch(
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
    if "postgres" not in container.enabled_modules:
        raise DisabledModuleError("postgres")

    result = await container.query_bus.dispatch(
        ListWorkflowsQuery(limit=limit, offset=offset)
    )
    return result.model_dump()
