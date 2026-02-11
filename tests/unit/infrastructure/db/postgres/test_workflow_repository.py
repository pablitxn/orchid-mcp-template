"""Unit tests for Postgres workflow repository adapter."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

import pytest

from sackmesser.infrastructure.db.postgres.workflow_repository import PostgresWorkflowRepository


class _FakePostgresProvider:
    def __init__(self) -> None:
        self.executescript_calls: list[str] = []
        self.fetchone_calls: list[tuple[str, tuple[object, ...]]] = []
        self.fetchall_calls: list[tuple[str, tuple[object, ...]]] = []
        self.fetchone_result: dict[str, Any] | None = None
        self.fetchall_result: list[dict[str, Any]] = []

    async def executescript(self, sql: str) -> None:
        self.executescript_calls.append(sql)

    async def fetchone(self, query: str, args: tuple[object, ...]) -> dict[str, Any] | None:
        self.fetchone_calls.append((query, args))
        return self.fetchone_result

    async def fetchall(self, query: str, args: tuple[object, ...]) -> list[dict[str, Any]]:
        self.fetchall_calls.append((query, args))
        return self.fetchall_result


async def test_ensure_schema_executes_create_table_script() -> None:
    provider = _FakePostgresProvider()
    repository = PostgresWorkflowRepository(provider)  # type: ignore[arg-type]

    await repository.ensure_schema()

    assert len(provider.executescript_calls) == 1
    assert "CREATE TABLE IF NOT EXISTS template_workflows" in provider.executescript_calls[0]


async def test_create_persists_and_maps_workflow(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = _FakePostgresProvider()
    provider.fetchone_result = {
        "id": "wf-1",
        "title": "demo",
        "payload": '{"kind":"smoke"}',
        "created_at": "2026-01-01T00:00:00Z",
    }
    repository = PostgresWorkflowRepository(provider)  # type: ignore[arg-type]
    monkeypatch.setattr(
        "sackmesser.infrastructure.db.postgres.workflow_repository.uuid.uuid4",
        lambda: SimpleNamespace(hex="fixed-uuid"),
    )

    workflow = await repository.create("demo", {"kind": "smoke"})

    assert workflow.id == "wf-1"
    assert workflow.title == "demo"
    assert workflow.payload == {"kind": "smoke"}
    assert workflow.created_at.tzinfo is not None

    query, args = provider.fetchone_calls[0]
    assert "INSERT INTO template_workflows" in query
    assert args[0] == "fixed-uuid"
    assert args[1] == "demo"
    assert args[2] == '{"kind": "smoke"}'


async def test_create_raises_when_insert_returns_no_row() -> None:
    provider = _FakePostgresProvider()
    provider.fetchone_result = None
    repository = PostgresWorkflowRepository(provider)  # type: ignore[arg-type]

    with pytest.raises(RuntimeError, match="Failed to insert workflow"):
        await repository.create("demo", {})


async def test_list_maps_multiple_row_shapes() -> None:
    provider = _FakePostgresProvider()
    provider.fetchall_result = [
        {
            "id": "wf-1",
            "title": "one",
            "payload": {"a": 1},
            "created_at": datetime(2026, 1, 1, tzinfo=UTC),
        },
        {
            "id": "wf-2",
            "title": "two",
            "payload": '{"b": 2}',
            "created_at": "2026-01-02T00:00:00Z",
        },
        {
            "id": "wf-3",
            "title": "three",
            "payload": 123,
            "created_at": None,
        },
    ]
    repository = PostgresWorkflowRepository(provider)  # type: ignore[arg-type]

    workflows = await repository.list(limit=10, offset=0)

    assert [item.id for item in workflows] == ["wf-1", "wf-2", "wf-3"]
    assert workflows[0].payload == {"a": 1}
    assert workflows[1].payload == {"b": 2}
    assert workflows[2].payload == {}
    assert all(item.created_at.tzinfo is not None for item in workflows)

    query, args = provider.fetchall_calls[0]
    assert "SELECT id, title, payload, created_at" in query
    assert args == (10, 0)
