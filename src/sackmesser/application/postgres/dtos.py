"""Postgres application DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class WorkflowDto(BaseModel):
    """Workflow projection for adapters."""

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
