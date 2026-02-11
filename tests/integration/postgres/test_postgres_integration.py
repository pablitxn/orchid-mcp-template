"""Postgres integration tests against local docker instance."""

from __future__ import annotations

import pytest
from orchid_commons import PostgresProvider, PostgresSettings

from sackmesser.infrastructure.postgres.workflow_repository import PostgresWorkflowRepository


@pytest.mark.integration
async def test_postgres_workflow_repository_integration() -> None:
    provider: PostgresProvider | None = None
    try:
        provider = await PostgresProvider.create(
            PostgresSettings(
                dsn="postgresql://orchid:orchid@localhost:5432/orchid_template",
                min_pool_size=1,
                max_pool_size=2,
                command_timeout_seconds=5.0,
            )
        )
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"Postgres not available: {exc}")

    try:
        repository = PostgresWorkflowRepository(provider)
        await repository.ensure_schema()
        created = await repository.create("integration-workflow", {"source": "pytest"})
        listed = await repository.list(limit=10, offset=0)

        assert created.title == "integration-workflow"
        assert any(item.id == created.id for item in listed)
    finally:
        await provider.close()
