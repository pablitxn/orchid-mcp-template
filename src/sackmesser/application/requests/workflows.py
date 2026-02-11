"""Workflow request/response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CreateWorkflowCommand(BaseModel):
    """Create a workflow aggregate."""

    model_config = ConfigDict(frozen=True)

    title: str = Field(min_length=1, max_length=200)
    payload: dict[str, Any] = Field(default_factory=dict)


class ListWorkflowsQuery(BaseModel):
    """List workflow aggregates."""

    model_config = ConfigDict(frozen=True)

    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class WorkflowDto(BaseModel):
    """Workflow aggregate projection."""

    model_config = ConfigDict(frozen=True)

    id: str
    title: str
    payload: dict[str, Any]
    created_at: datetime


class CreateWorkflowResult(BaseModel):
    """Result wrapper for create workflow."""

    model_config = ConfigDict(frozen=True)

    workflow: WorkflowDto


class ListWorkflowsResult(BaseModel):
    """Result wrapper for workflow listing."""

    model_config = ConfigDict(frozen=True)

    workflows: list[WorkflowDto]
