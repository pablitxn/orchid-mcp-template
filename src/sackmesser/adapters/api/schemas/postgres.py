"""Schemas for Postgres workflow routes."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CreateWorkflowRequest(BaseModel):
    """Request payload for creating workflow."""

    title: str = Field(min_length=1, max_length=200)
    payload: dict[str, Any] = Field(default_factory=dict)
