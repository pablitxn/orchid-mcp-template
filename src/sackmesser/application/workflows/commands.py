"""Workflow command models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CreateWorkflowCommand(BaseModel):
    """Create a workflow aggregate."""

    model_config = ConfigDict(frozen=True)

    title: str = Field(min_length=1, max_length=200)
    payload: dict[str, Any] = Field(default_factory=dict)
