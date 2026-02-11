"""Postgres-specific infrastructure adapters."""

from sackmesser.infrastructure.db.postgres.workflow_repository import (
    PostgresWorkflowRepository,
)

__all__ = ["PostgresWorkflowRepository"]
