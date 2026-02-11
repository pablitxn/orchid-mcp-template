"""Application request/response model exports."""

from importlib import import_module

from sackmesser.application.requests.core import (
    CapabilityDto,
    GetCapabilitiesQuery,
    GetCapabilitiesResult,
    GetHealthQuery,
    GetHealthResult,
)

__all__ = [
    "CapabilityDto",
    "GetCapabilitiesQuery",
    "GetCapabilitiesResult",
    "GetHealthQuery",
    "GetHealthResult",
]

_OPTIONAL_EXPORTS: dict[str, tuple[str, ...]] = {
    "sackmesser.application.requests.workflows": (
        "CreateWorkflowCommand",
        "CreateWorkflowResult",
        "ListWorkflowsQuery",
        "ListWorkflowsResult",
        "WorkflowDto",
    ),
    "sackmesser.application.requests.cache": (
        "CacheEntryDto",
        "DeleteCacheEntryCommand",
        "DeleteCacheEntryResult",
        "GetCacheEntryQuery",
        "GetCacheEntryResult",
        "SetCacheEntryCommand",
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
