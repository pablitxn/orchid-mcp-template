"""Unit tests for runtime container wiring."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import ClassVar

from sackmesser.application.requests.cache import (
    DeleteCacheEntryCommand,
    GetCacheEntryQuery,
    SetCacheEntryCommand,
)
from sackmesser.application.requests.core import GetCapabilitiesQuery, GetHealthQuery
from sackmesser.application.requests.workflows import (
    CreateWorkflowCommand,
    ListWorkflowsQuery,
)
from sackmesser.domain.cache import CacheEntry
from sackmesser.domain.workflows import Workflow
from sackmesser.infrastructure.runtime.container import build_container
from sackmesser.infrastructure.runtime.modules import ModuleMetadata


class _FakeManager:
    def __init__(self, *, providers: dict[str, object] | None = None) -> None:
        self.providers = {} if providers is None else providers
        self.get_calls: list[str] = []

    def get(self, name: str) -> object:
        self.get_calls.append(name)
        return self.providers[name]

    async def health_payload(self) -> dict[str, object]:
        return {"status": "ok", "checks": {"runtime": "ok"}}


def _manifest() -> dict[str, ModuleMetadata]:
    return {
        "core": ModuleMetadata(
            name="core",
            description="Core module",
            required=True,
            resources=(),
        ),
        "postgres": ModuleMetadata(
            name="postgres",
            description="Postgres module",
            required=False,
            resources=("postgres",),
        ),
        "redis": ModuleMetadata(
            name="redis",
            description="Redis module",
            required=False,
            resources=("redis",),
        ),
    }


async def test_build_container_core_handlers_work() -> None:
    manager = _FakeManager()

    container = await build_container(
        settings=SimpleNamespace(service=SimpleNamespace(name="svc")),
        enabled_modules=frozenset({"core"}),
        module_manifest=_manifest(),
        manager=manager,
    )

    health = await container.query_bus.dispatch(GetHealthQuery())
    capabilities = await container.query_bus.dispatch(GetCapabilitiesQuery())
    capabilities_by_name = {item.name: item for item in capabilities.capabilities}

    assert health.status == "ok"
    assert capabilities_by_name["core"].enabled is True
    assert capabilities_by_name["postgres"].enabled is False
    assert capabilities_by_name["redis"].enabled is False
    assert manager.get_calls == []


async def test_build_container_registers_postgres_and_redis_handlers(monkeypatch) -> None:
    class _FakePostgresWorkflowRepository:
        instances: ClassVar[list[_FakePostgresWorkflowRepository]] = []

        def __init__(self, provider: object) -> None:
            self.provider = provider
            self.ensure_schema_called = False
            self.items: list[Workflow] = []
            self.__class__.instances.append(self)

        async def ensure_schema(self) -> None:
            self.ensure_schema_called = True

        async def create(self, title: str, payload: dict[str, object]) -> Workflow:
            workflow = Workflow(
                id=f"wf-{len(self.items)+1}",
                title=title,
                payload=dict(payload),
                created_at=datetime(2026, 1, 1, tzinfo=UTC),
            )
            self.items.append(workflow)
            return workflow

        async def list(self, *, limit: int, offset: int) -> list[Workflow]:
            return self.items[offset : offset + limit]

    class _FakeRedisCacheRepository:
        def __init__(self, cache: object) -> None:
            self.cache = cache
            self.store: dict[str, str] = {}

        async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> bool:
            del ttl_seconds
            self.store[key] = value
            return True

        async def get(self, key: str) -> CacheEntry:
            return CacheEntry(key=key, value=self.store.get(key))

        async def delete(self, key: str) -> bool:
            return self.store.pop(key, None) is not None

    monkeypatch.setattr(
        "sackmesser.infrastructure.db.postgres.workflow_repository.PostgresWorkflowRepository",
        _FakePostgresWorkflowRepository,
    )
    monkeypatch.setattr(
        "sackmesser.infrastructure.db.redis.cache_repository.RedisCacheRepository",
        _FakeRedisCacheRepository,
    )

    postgres_provider = object()
    redis_provider = object()
    manager = _FakeManager(providers={"postgres": postgres_provider, "redis": redis_provider})

    container = await build_container(
        settings=SimpleNamespace(service=SimpleNamespace(name="svc")),
        enabled_modules=frozenset({"core", "postgres", "redis"}),
        module_manifest=_manifest(),
        manager=manager,
    )

    created = await container.command_bus.dispatch(
        CreateWorkflowCommand(title="demo", payload={"kind": "smoke"})
    )
    listed = await container.query_bus.dispatch(ListWorkflowsQuery(limit=10, offset=0))
    set_result = await container.command_bus.dispatch(
        SetCacheEntryCommand(key="alpha", value="1")
    )
    got = await container.query_bus.dispatch(GetCacheEntryQuery(key="alpha"))
    deleted = await container.command_bus.dispatch(DeleteCacheEntryCommand(key="alpha"))

    assert created.workflow.title == "demo"
    assert len(listed.workflows) == 1
    assert set_result.success is True
    assert got.entry.value == "1"
    assert deleted.success is True
    assert manager.get_calls == ["postgres", "redis"]
    assert _FakePostgresWorkflowRepository.instances[0].provider is postgres_provider
    assert _FakePostgresWorkflowRepository.instances[0].ensure_schema_called is True
