"""Postgres-related hexagonal ports."""

from __future__ import annotations

from typing import Protocol

from sackmesser.domain.postgres.entities import Workflow


class WorkflowRepositoryPort(Protocol):
    """Persistence contract for workflow aggregate."""

    async def create(self, title: str, payload: dict[str, object]) -> Workflow:
        """Persist a workflow and return stored entity."""

    async def list(self, *, limit: int, offset: int) -> list[Workflow]:
        """List workflows in reverse creation order."""
