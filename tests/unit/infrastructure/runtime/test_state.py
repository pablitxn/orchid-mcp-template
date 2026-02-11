"""Unit tests for runtime state lifecycle."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from sackmesser.infrastructure.runtime import state as runtime_state
from sackmesser.infrastructure.runtime.modules import ModuleMetadata


@pytest.fixture(autouse=True)
def _reset_runtime_holder() -> None:
    runtime_state.reset_runtime_state_for_tests()
    yield
    runtime_state.reset_runtime_state_for_tests()


class _FakeManager:
    def __init__(self) -> None:
        self.startup_calls: list[tuple[object, list[str]]] = []
        self.close_all_calls = 0

    async def startup(self, resource_settings: object, *, required: list[str]) -> None:
        self.startup_calls.append((resource_settings, required))

    async def close_all(self) -> None:
        self.close_all_calls += 1


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
        "blob": ModuleMetadata(
            name="blob",
            description="Blob module",
            required=False,
            resources=("minio",),
        ),
    }


def test_resolve_environment_prefers_explicit_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORCHID_ENV", "prod")
    assert runtime_state.resolve_environment("staging") == "staging"


def test_resolve_environment_reads_env_and_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORCHID_ENV", "test")
    assert runtime_state.resolve_environment() == "test"

    monkeypatch.delenv("ORCHID_ENV", raising=False)
    assert runtime_state.resolve_environment() == runtime_state.DEFAULT_ENV


def test_filter_resource_settings_disables_non_enabled_modules() -> None:
    settings = runtime_state.RuntimeResourceSettings(
        sqlite="sqlite",
        postgres="pg",
        redis="redis",
        mongodb="mongo",
        rabbitmq="rabbit",
        qdrant="qdrant",
        minio="minio",
        r2="r2",
        pgvector="pgvector",
        multi_bucket="bucket",
    )

    filtered = runtime_state._filter_resource_settings(
        settings,
        frozenset({"core", "postgres", "blob"}),
    )

    assert filtered.postgres == "pg"
    assert filtered.pgvector == "pgvector"
    assert filtered.minio == "minio"
    assert filtered.r2 == "r2"
    assert filtered.multi_bucket == "bucket"
    assert filtered.redis is None
    assert filtered.mongodb is None
    assert filtered.rabbitmq is None
    assert filtered.qdrant is None


async def test_startup_runtime_returns_existing_state() -> None:
    existing = runtime_state.RuntimeState(
        settings=SimpleNamespace(),
        enabled_modules=frozenset({"core"}),
        module_manifest={},
        manager=_FakeManager(),
        container=SimpleNamespace(name="container"),
        environment="existing",
    )
    runtime_state._RuntimeHolder.state = existing

    result = await runtime_state.startup_runtime()

    assert result is existing


async def test_startup_runtime_bootstraps_state_and_reuses_cached_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = SimpleNamespace(
        resources=SimpleNamespace(
            sqlite="sqlite",
            postgres="pg",
            redis="redis",
            mongodb="mongo",
            rabbitmq="rabbit",
            qdrant="qdrant",
            minio="minio",
            r2="r2",
            multi_bucket="bucket",
        )
    )
    manifest = _manifest()
    manager_instances: list[_FakeManager] = []
    load_config_calls: list[tuple[object, str]] = []
    bootstrap_calls: list[str] = []
    build_container_calls: list[dict[str, object]] = []
    container = SimpleNamespace(name="container")

    def fake_load_config(*, config_dir: object, env: str) -> object:
        load_config_calls.append((config_dir, env))
        return settings

    def fake_bootstrap(config: object, *, env: str) -> None:
        assert config is settings
        bootstrap_calls.append(env)

    def fake_resource_manager() -> _FakeManager:
        manager = _FakeManager()
        manager_instances.append(manager)
        return manager

    async def fake_build_container(**kwargs: object) -> object:
        build_container_calls.append(kwargs)
        return container

    monkeypatch.setattr("sackmesser.infrastructure.runtime.state.load_config", fake_load_config)
    monkeypatch.setattr(
        "sackmesser.infrastructure.runtime.state.bootstrap_logging_from_app_settings",
        fake_bootstrap,
    )
    monkeypatch.setattr(
        "sackmesser.infrastructure.runtime.state.load_module_manifest",
        lambda: manifest,
    )
    monkeypatch.setattr(
        "sackmesser.infrastructure.runtime.state.load_enabled_modules",
        lambda: {"postgres", "blob"},
    )
    monkeypatch.setattr(
        "sackmesser.infrastructure.runtime.state.resolve_enabled_modules",
        lambda selected, loaded_manifest: frozenset({"core", *selected}),
    )
    monkeypatch.setattr(
        "sackmesser.infrastructure.runtime.state.required_resource_names",
        lambda enabled: sorted(
            resource
            for module in enabled
            for resource in manifest[module].resources
        ),
    )
    monkeypatch.setattr("sackmesser.infrastructure.runtime.state.ResourceManager", fake_resource_manager)
    monkeypatch.setattr("sackmesser.infrastructure.runtime.state.build_container", fake_build_container)

    result = await runtime_state.startup_runtime(env="staging")

    assert result.environment == "staging"
    assert result.settings is settings
    assert result.enabled_modules == frozenset({"core", "postgres", "blob"})
    assert result.module_manifest is manifest
    assert result.container is container
    assert load_config_calls == [(runtime_state.CONFIG_DIR, "staging")]
    assert bootstrap_calls == ["staging"]
    assert len(manager_instances) == 1

    manager = manager_instances[0]
    assert len(manager.startup_calls) == 1
    selected_resource_settings, required_resources = manager.startup_calls[0]
    assert required_resources == ["minio", "postgres"]
    assert isinstance(selected_resource_settings, runtime_state.RuntimeResourceSettings)
    assert selected_resource_settings.postgres == "pg"
    assert selected_resource_settings.redis is None
    assert selected_resource_settings.minio == "minio"
    assert selected_resource_settings.r2 == "r2"

    assert len(build_container_calls) == 1
    assert build_container_calls[0]["settings"] is settings
    assert build_container_calls[0]["enabled_modules"] == frozenset({"core", "postgres", "blob"})
    assert build_container_calls[0]["module_manifest"] is manifest
    assert build_container_calls[0]["manager"] is manager

    assert runtime_state.get_runtime_state() is result
    assert runtime_state.get_runtime_container() is container

    cached_result = await runtime_state.startup_runtime(env="other")
    assert cached_result is result
    assert load_config_calls == [(runtime_state.CONFIG_DIR, "staging")]
    assert len(manager.startup_calls) == 1


async def test_shutdown_runtime_closes_manager_and_clears_state() -> None:
    manager = _FakeManager()
    runtime_state._RuntimeHolder.state = runtime_state.RuntimeState(
        settings=SimpleNamespace(),
        enabled_modules=frozenset({"core"}),
        module_manifest={},
        manager=manager,
        container=SimpleNamespace(),
        environment="test",
    )

    await runtime_state.shutdown_runtime()

    assert manager.close_all_calls == 1
    assert runtime_state._RuntimeHolder.state is None


async def test_shutdown_runtime_is_noop_when_not_initialized() -> None:
    await runtime_state.shutdown_runtime()
    assert runtime_state._RuntimeHolder.state is None


def test_get_runtime_state_raises_when_runtime_not_initialized() -> None:
    with pytest.raises(RuntimeError, match="Runtime is not initialized"):
        runtime_state.get_runtime_state()


def test_reset_runtime_state_for_tests_clears_state() -> None:
    runtime_state._RuntimeHolder.state = runtime_state.RuntimeState(
        settings=SimpleNamespace(),
        enabled_modules=frozenset({"core"}),
        module_manifest={},
        manager=_FakeManager(),
        container=SimpleNamespace(),
        environment="test",
    )

    runtime_state.reset_runtime_state_for_tests()

    assert runtime_state._RuntimeHolder.state is None
