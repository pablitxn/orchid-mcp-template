"""Application layer exports."""

from importlib import import_module

from sackmesser.application.bus import (
    CommandBus,
    Handler,
    HandlerNotRegisteredError,
    QueryBus,
)
from sackmesser.application.core import (
    CapabilityDto,
    GetCapabilitiesHandler,
    GetCapabilitiesQueryHandler,
    GetCapabilitiesQuery,
    GetCapabilitiesResult,
    GetHealthHandler,
    GetHealthQueryHandler,
    GetHealthQuery,
    GetHealthResult,
)
from sackmesser.application.errors import (
    ApplicationError,
    ConflictError,
    DisabledModuleError,
    NotFoundError,
    ValidationError,
)

__all__ = [
    "ApplicationError",
    "CommandBus",
    "CapabilityDto",
    "ConflictError",
    "DisabledModuleError",
    "GetCapabilitiesHandler",
    "GetCapabilitiesQueryHandler",
    "GetCapabilitiesQuery",
    "GetCapabilitiesResult",
    "GetHealthHandler",
    "GetHealthQueryHandler",
    "GetHealthQuery",
    "GetHealthResult",
    "Handler",
    "HandlerNotRegisteredError",
    "NotFoundError",
    "QueryBus",
    "ValidationError",
]

_OPTIONAL_EXPORTS: dict[str, tuple[str, ...]] = {
    "sackmesser.application.workflows": (
        "CreateWorkflowCommand",
        "CreateWorkflowCommandHandler",
        "CreateWorkflowHandler",
        "CreateWorkflowResult",
        "ListWorkflowsHandler",
        "ListWorkflowsQuery",
        "ListWorkflowsQueryHandler",
        "ListWorkflowsResult",
    ),
    "sackmesser.application.cache": (
        "DeleteCacheEntryCommand",
        "DeleteCacheEntryCommandHandler",
        "DeleteCacheEntryHandler",
        "DeleteCacheEntryResult",
        "GetCacheEntryHandler",
        "GetCacheEntryQuery",
        "GetCacheEntryQueryHandler",
        "GetCacheEntryResult",
        "SetCacheEntryCommand",
        "SetCacheEntryCommandHandler",
        "SetCacheEntryHandler",
        "SetCacheEntryResult",
    ),
}

for module_name, export_names in _OPTIONAL_EXPORTS.items():
    try:
        module = import_module(module_name)
    except ModuleNotFoundError:
        continue
    for export_name in export_names:
        globals()[export_name] = getattr(module, export_name)
    __all__.extend(export_names)
