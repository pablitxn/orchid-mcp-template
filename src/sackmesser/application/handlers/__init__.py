"""Application handler exports."""

from importlib import import_module

from sackmesser.application.handlers.core import (
    GetCapabilitiesQueryHandler,
    GetHealthQueryHandler,
)

__all__ = ["GetCapabilitiesQueryHandler", "GetHealthQueryHandler"]

_OPTIONAL_EXPORTS: dict[str, tuple[str, ...]] = {
    "sackmesser.application.handlers.workflows": (
        "CreateWorkflowCommandHandler",
        "ListWorkflowsQueryHandler",
    ),
    "sackmesser.application.handlers.cache": (
        "DeleteCacheEntryCommandHandler",
        "GetCacheEntryQueryHandler",
        "SetCacheEntryCommandHandler",
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
