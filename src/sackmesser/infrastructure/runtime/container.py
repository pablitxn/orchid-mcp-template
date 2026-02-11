"""Application container wiring handlers to infrastructure adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from orchid_commons import PostgresProvider, RedisCache, ResourceManager
from orchid_commons.config.models import AppSettings

from sackmesser.application.bus import CommandBus, QueryBus
from sackmesser.application.handlers.core import (
    GetCapabilitiesQueryHandler,
    GetHealthQueryHandler,
)
from sackmesser.application.requests.core import (
    GetCapabilitiesQuery,
    GetHealthQuery,
)
from sackmesser.infrastructure.core.capability_provider import ManifestCapabilityProvider
from sackmesser.infrastructure.core.health_provider import ResourceManagerHealthProvider
from sackmesser.infrastructure.runtime.modules import ModuleMetadata


@dataclass(slots=True)
class ApplicationContainer:
    """Dependency graph exposed to API/MCP adapters."""

    settings: AppSettings
    enabled_modules: frozenset[str]
    resource_manager: ResourceManager
    command_bus: CommandBus
    query_bus: QueryBus


async def build_container(
    *,
    settings: AppSettings,
    enabled_modules: frozenset[str],
    module_manifest: dict[str, ModuleMetadata],
    manager: ResourceManager,
) -> ApplicationContainer:
    """Build app container from runtime resources + module selection."""
    capability_port = ManifestCapabilityProvider(
        manifest=module_manifest,
        enabled_modules=enabled_modules,
    )
    health_port = ResourceManagerHealthProvider(manager)

    command_bus = CommandBus()
    query_bus = QueryBus()

    query_bus.register(
        GetCapabilitiesQuery,
        GetCapabilitiesQueryHandler(capability_port),
    )
    query_bus.register(GetHealthQuery, GetHealthQueryHandler(health_port))

    if "postgres" in enabled_modules:
        from sackmesser.application.handlers.workflows import (
            CreateWorkflowCommandHandler,
            ListWorkflowsQueryHandler,
        )
        from sackmesser.application.requests.workflows import (
            CreateWorkflowCommand,
            ListWorkflowsQuery,
        )
        from sackmesser.infrastructure.db.postgres.workflow_repository import (
            PostgresWorkflowRepository,
        )

        provider = cast("PostgresProvider", manager.get("postgres"))
        workflow_repository = PostgresWorkflowRepository(provider)
        await workflow_repository.ensure_schema()

        command_bus.register(
            CreateWorkflowCommand,
            CreateWorkflowCommandHandler(workflow_repository),
        )
        query_bus.register(
            ListWorkflowsQuery,
            ListWorkflowsQueryHandler(workflow_repository),
        )

    if "redis" in enabled_modules:
        from sackmesser.application.handlers.cache import (
            DeleteCacheEntryCommandHandler,
            GetCacheEntryQueryHandler,
            SetCacheEntryCommandHandler,
        )
        from sackmesser.application.requests.cache import (
            DeleteCacheEntryCommand,
            GetCacheEntryQuery,
            SetCacheEntryCommand,
        )
        from sackmesser.infrastructure.db.redis.cache_repository import (
            RedisCacheRepository,
        )

        redis_cache = cast("RedisCache", manager.get("redis"))
        cache_repository = RedisCacheRepository(redis_cache)

        command_bus.register(
            SetCacheEntryCommand,
            SetCacheEntryCommandHandler(cache_repository),
        )
        query_bus.register(
            GetCacheEntryQuery,
            GetCacheEntryQueryHandler(cache_repository),
        )
        command_bus.register(
            DeleteCacheEntryCommand,
            DeleteCacheEntryCommandHandler(cache_repository),
        )

    return ApplicationContainer(
        settings=settings,
        enabled_modules=enabled_modules,
        resource_manager=manager,
        command_bus=command_bus,
        query_bus=query_bus,
    )
