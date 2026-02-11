"""Postgres repository adapter for workflow aggregate."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from orchid_commons import PostgresProvider

from sackmesser.domain.ports.workflow_ports import WorkflowRepositoryPort
from sackmesser.domain.workflows.entities import Workflow

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS template_workflows (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


class PostgresWorkflowRepository(WorkflowRepositoryPort):
    """Persist workflow entities using commons PostgresProvider."""

    def __init__(self, provider: PostgresProvider) -> None:
        self._provider = provider

    async def ensure_schema(self) -> None:
        """Create required table for workflow example."""
        await self._provider.executescript(_SCHEMA_SQL)

    async def create(self, title: str, payload: dict[str, object]) -> Workflow:
        workflow_id = uuid.uuid4().hex
        row = await self._provider.fetchone(
            """
            INSERT INTO template_workflows (id, title, payload)
            VALUES ($1, $2, $3::jsonb)
            RETURNING id, title, payload, created_at
            """,
            (workflow_id, title, json.dumps(payload)),
        )
        if row is None:
            msg = "Failed to insert workflow"
            raise RuntimeError(msg)
        return _to_workflow(row)

    async def list(self, *, limit: int, offset: int) -> list[Workflow]:
        rows = await self._provider.fetchall(
            """
            SELECT id, title, payload, created_at
            FROM template_workflows
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
            """,
            (limit, offset),
        )
        return [_to_workflow(row) for row in rows]


def _to_workflow(row: dict[str, Any]) -> Workflow:
    payload_raw = row.get("payload")
    payload = _coerce_payload(payload_raw)

    created_at_raw = row.get("created_at")
    created_at = _coerce_datetime(created_at_raw)

    return Workflow(
        id=str(row["id"]),
        title=str(row["title"]),
        payload=payload,
        created_at=created_at,
    )


def _coerce_payload(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        parsed = json.loads(value)
        if isinstance(parsed, dict):
            return parsed
    return {}


def _coerce_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    if isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)
    return datetime.now(tz=UTC)
