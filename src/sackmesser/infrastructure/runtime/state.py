"""Runtime startup/shutdown lifecycle."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from orchid_commons import (
    ResourceManager,
    bootstrap_logging_from_app_settings,
    load_config,
)
from orchid_commons.config.models import AppSettings

from sackmesser.infrastructure.runtime.container import ApplicationContainer, build_container
from sackmesser.infrastructure.runtime.modules import (
    ModuleMetadata,
    load_enabled_modules,
    load_module_manifest,
    required_resource_names,
    resolve_enabled_modules,
)

CONFIG_DIR = Path("config")
DEFAULT_ENV = "development"


@dataclass(slots=True)
class RuntimeResourceSettings:
    """Duck-typed settings object expected by commons ResourceManager bootstrap."""

    sqlite: object | None = None
    postgres: object | None = None
    redis: object | None = None
    mongodb: object | None = None
    rabbitmq: object | None = None
    qdrant: object | None = None
    minio: object | None = None
    r2: object | None = None
    pgvector: object | None = None
    multi_bucket: object | None = None


@dataclass(slots=True)
class RuntimeState:
    """Active runtime state."""

    settings: AppSettings
    enabled_modules: frozenset[str]
    module_manifest: dict[str, ModuleMetadata]
    manager: ResourceManager
    container: ApplicationContainer
    environment: str


class _RuntimeHolder:
    state: RuntimeState | None = None


def resolve_environment(env: str | None = None) -> str:
    """Resolve target environment using ORCHID_ENV fallback."""
    if env:
        return env
    return os.environ.get("ORCHID_ENV", DEFAULT_ENV)


def _filter_resource_settings(
    settings: RuntimeResourceSettings,
    enabled_modules: frozenset[str],
) -> RuntimeResourceSettings:
    return RuntimeResourceSettings(
        sqlite=settings.sqlite,
        postgres=settings.postgres if "postgres" in enabled_modules else None,
        redis=settings.redis if "redis" in enabled_modules else None,
        mongodb=settings.mongodb if "mongodb" in enabled_modules else None,
        rabbitmq=settings.rabbitmq if "rabbitmq" in enabled_modules else None,
        qdrant=settings.qdrant if "qdrant" in enabled_modules else None,
        minio=settings.minio if "blob" in enabled_modules else None,
        r2=settings.r2 if "blob" in enabled_modules else None,
        pgvector=settings.pgvector if "postgres" in enabled_modules else None,
        multi_bucket=settings.multi_bucket if "blob" in enabled_modules else None,
    )


def _resources_from_app_settings(settings: AppSettings) -> RuntimeResourceSettings:
    resources = settings.resources
    return RuntimeResourceSettings(
        sqlite=resources.sqlite,
        postgres=resources.postgres,
        redis=resources.redis,
        mongodb=resources.mongodb,
        rabbitmq=resources.rabbitmq,
        qdrant=resources.qdrant,
        minio=resources.minio,
        r2=resources.r2,
        multi_bucket=resources.multi_bucket,
    )


async def startup_runtime(*, env: str | None = None) -> RuntimeState:
    """Initialize settings, resources and container once."""
    existing = _RuntimeHolder.state
    if existing is not None:
        return existing

    environment = resolve_environment(env)
    settings = load_config(config_dir=CONFIG_DIR, env=environment)
    bootstrap_logging_from_app_settings(settings, env=environment)

    module_manifest = load_module_manifest()
    selected_modules = load_enabled_modules()
    enabled_modules = resolve_enabled_modules(selected_modules, module_manifest)

    resource_settings = _resources_from_app_settings(settings)
    selected_resource_settings = _filter_resource_settings(resource_settings, enabled_modules)

    manager = ResourceManager()
    required_resources = required_resource_names(enabled_modules)
    await manager.startup(cast(Any, selected_resource_settings), required=required_resources)

    container = await build_container(
        settings=settings,
        enabled_modules=enabled_modules,
        module_manifest=module_manifest,
        manager=manager,
    )

    state = RuntimeState(
        settings=settings,
        enabled_modules=enabled_modules,
        module_manifest=module_manifest,
        manager=manager,
        container=container,
        environment=environment,
    )
    _RuntimeHolder.state = state
    return state


async def shutdown_runtime() -> None:
    """Shutdown resources and clear runtime holder."""
    state = _RuntimeHolder.state
    _RuntimeHolder.state = None
    if state is None:
        return
    await state.manager.close_all()


def get_runtime_state() -> RuntimeState:
    """Return active runtime state."""
    state = _RuntimeHolder.state
    if state is None:
        msg = "Runtime is not initialized. Call startup_runtime() first."
        raise RuntimeError(msg)
    return state


def get_runtime_container() -> ApplicationContainer:
    """Return application container from active runtime."""
    return get_runtime_state().container


def reset_runtime_state_for_tests() -> None:
    """Reset state holder for isolated tests."""
    _RuntimeHolder.state = None
