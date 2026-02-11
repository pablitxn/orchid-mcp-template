"""Application container wiring use cases to infrastructure adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from orchid_commons import PostgresProvider, RedisCache, ResourceManager
from orchid_commons.config.models import AppSettings

from sackmesser.application.core import (
    GetCapabilitiesHandler,
    GetCapabilitiesUseCase,
    GetHealthHandler,
    GetHealthUseCase,
)
from sackmesser.infrastructure.core.capability_provider import ManifestCapabilityProvider
from sackmesser.infrastructure.core.health_provider import ResourceManagerHealthProvider
from sackmesser.infrastructure.runtime.modules import ModuleMetadata

if TYPE_CHECKING:
    from sackmesser.application.postgres import (
        CreateWorkflowHandler,
        ListWorkflowsHandler,
    )
    from sackmesser.application.redis import (
        DeleteCacheEntryHandler,
        GetCacheEntryHandler,
        SetCacheEntryHandler,
    )


@dataclass(slots=True)
class ApplicationContainer:
    """Dependency graph exposed to API/MCP adapters."""

    settings: AppSettings
    enabled_modules: frozenset[str]
    resource_manager: ResourceManager

    get_health_handler: GetHealthHandler
    get_capabilities_handler: GetCapabilitiesHandler

    create_workflow_handler: CreateWorkflowHandler | None = None
    list_workflows_handler: ListWorkflowsHandler | None = None

    set_cache_entry_handler: SetCacheEntryHandler | None = None
    get_cache_entry_handler: GetCacheEntryHandler | None = None
    delete_cache_entry_handler: DeleteCacheEntryHandler | None = None


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

    container = ApplicationContainer(
        settings=settings,
        enabled_modules=enabled_modules,
        resource_manager=manager,
        get_capabilities_handler=GetCapabilitiesHandler(
            GetCapabilitiesUseCase(capability_port)
        ),
        get_health_handler=GetHealthHandler(GetHealthUseCase(health_port)),
    )

    if "postgres" in enabled_modules:
        from sackmesser.application.postgres import (
            CreateWorkflowHandler,
            CreateWorkflowUseCase,
            ListWorkflowsHandler,
            ListWorkflowsUseCase,
        )
        from sackmesser.infrastructure.postgres.workflow_repository import (
            PostgresWorkflowRepository,
        )

        provider = cast("PostgresProvider", manager.get("postgres"))
        workflow_repository = PostgresWorkflowRepository(provider)
        await workflow_repository.ensure_schema()

        container.create_workflow_handler = CreateWorkflowHandler(
            CreateWorkflowUseCase(workflow_repository)
        )
        container.list_workflows_handler = ListWorkflowsHandler(
            ListWorkflowsUseCase(workflow_repository)
        )

    if "redis" in enabled_modules:
        from sackmesser.application.redis import (
            DeleteCacheEntryHandler,
            DeleteCacheEntryUseCase,
            GetCacheEntryHandler,
            GetCacheEntryUseCase,
            SetCacheEntryHandler,
            SetCacheEntryUseCase,
        )
        from sackmesser.infrastructure.redis.cache_repository import RedisCacheRepository

        redis_cache = cast("RedisCache", manager.get("redis"))
        cache_repository = RedisCacheRepository(redis_cache)

        container.set_cache_entry_handler = SetCacheEntryHandler(
            SetCacheEntryUseCase(cache_repository)
        )
        container.get_cache_entry_handler = GetCacheEntryHandler(
            GetCacheEntryUseCase(cache_repository)
        )
        container.delete_cache_entry_handler = DeleteCacheEntryHandler(
            DeleteCacheEntryUseCase(cache_repository)
        )

    return container
