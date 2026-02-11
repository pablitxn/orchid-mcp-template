"""Application layer exports."""

from importlib import import_module

from sackmesser.application.core import (
    CapabilityDto,
    GetCapabilitiesHandler,
    GetCapabilitiesQuery,
    GetCapabilitiesResult,
    GetHealthHandler,
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
    "CapabilityDto",
    "ConflictError",
    "DisabledModuleError",
    "GetCapabilitiesHandler",
    "GetCapabilitiesQuery",
    "GetCapabilitiesResult",
    "GetHealthHandler",
    "GetHealthQuery",
    "GetHealthResult",
    "NotFoundError",
    "ValidationError",
]

_OPTIONAL_EXPORTS: dict[str, tuple[str, ...]] = {
    "sackmesser.application.postgres": (
        "CreateWorkflowCommand",
        "CreateWorkflowHandler",
        "CreateWorkflowResult",
        "ListWorkflowsHandler",
        "ListWorkflowsQuery",
        "ListWorkflowsResult",
    ),
    "sackmesser.application.redis": (
        "DeleteCacheEntryCommand",
        "DeleteCacheEntryHandler",
        "DeleteCacheEntryResult",
        "GetCacheEntryHandler",
        "GetCacheEntryQuery",
        "GetCacheEntryResult",
        "SetCacheEntryCommand",
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
