"""Postgres workflow API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from sackmesser.adapters.dependencies import ContainerDep
from sackmesser.application.postgres import CreateWorkflowCommand, ListWorkflowsQuery

router = APIRouter(prefix="/api/v1/workflows")


class CreateWorkflowRequest(BaseModel):
    """Request payload for creating workflow."""

    title: str = Field(min_length=1, max_length=200)
    payload: dict[str, Any] = Field(default_factory=dict)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workflow(
    body: CreateWorkflowRequest,
    container: ContainerDep,
) -> dict[str, Any]:
    """Create a workflow in Postgres."""
    handler = container.create_workflow_handler
    if handler is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Postgres module is disabled",
        )

    result = await handler.handle(
        CreateWorkflowCommand(title=body.title, payload=body.payload)
    )
    return result.model_dump()


@router.get("")
async def list_workflows(
    container: ContainerDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    """List workflows from Postgres."""
    handler = container.list_workflows_handler
    if handler is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Postgres module is disabled",
        )

    result = await handler.handle(ListWorkflowsQuery(limit=limit, offset=offset))
    return result.model_dump()
