"""Application layer exports."""

from importlib import import_module

from sackmesser.application.bus import CommandBus, Handler, HandlerNotRegisteredError, QueryBus
from sackmesser.application.errors import (
    ApplicationError,
    ConflictError,
    DisabledModuleError,
    NotFoundError,
    ValidationError,
)
from sackmesser.application.handlers.core import (
    GetCapabilitiesQueryHandler,
    GetHealthQueryHandler,
)
from sackmesser.application.requests.core import (
    CapabilityDto,
    GetCapabilitiesQuery,
    GetCapabilitiesResult,
    GetHealthQuery,
    GetHealthResult,
)
from sackmesser.application.use_cases.base import BaseUseCase, UseCase
from sackmesser.application.use_cases.core import GetCapabilitiesUseCase, GetHealthUseCase

# Backward-compatible aliases
GetCapabilitiesHandler = GetCapabilitiesQueryHandler
GetHealthHandler = GetHealthQueryHandler

__all__ = [
    "ApplicationError",
    "BaseUseCase",
    "CapabilityDto",
    "CommandBus",
    "ConflictError",
    "DisabledModuleError",
    "GetCapabilitiesHandler",
    "GetCapabilitiesQuery",
    "GetCapabilitiesQueryHandler",
    "GetCapabilitiesResult",
    "GetCapabilitiesUseCase",
    "GetHealthHandler",
    "GetHealthQuery",
    "GetHealthQueryHandler",
    "GetHealthResult",
    "GetHealthUseCase",
    "Handler",
    "HandlerNotRegisteredError",
    "NotFoundError",
    "QueryBus",
    "UseCase",
    "ValidationError",
]

_OPTIONAL_EXPORTS: dict[str, tuple[str, ...]] = {
    "sackmesser.application.requests.workflows": (
        "CreateWorkflowCommand",
        "CreateWorkflowResult",
        "ListWorkflowsQuery",
        "ListWorkflowsResult",
        "WorkflowDto",
    ),
    "sackmesser.application.handlers.workflows": (
        "CreateWorkflowCommandHandler",
        "ListWorkflowsQueryHandler",
    ),
    "sackmesser.application.use_cases.workflows": (
        "CreateWorkflowUseCase",
        "ListWorkflowsUseCase",
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
    "sackmesser.application.handlers.cache": (
        "DeleteCacheEntryCommandHandler",
        "GetCacheEntryQueryHandler",
        "SetCacheEntryCommandHandler",
    ),
    "sackmesser.application.use_cases.cache": (
        "DeleteCacheEntryUseCase",
        "GetCacheEntryUseCase",
        "SetCacheEntryUseCase",
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

if "CreateWorkflowCommandHandler" in globals():
    globals()["CreateWorkflowHandler"] = globals()["CreateWorkflowCommandHandler"]
    __all__.append("CreateWorkflowHandler")
if "ListWorkflowsQueryHandler" in globals():
    globals()["ListWorkflowsHandler"] = globals()["ListWorkflowsQueryHandler"]
    __all__.append("ListWorkflowsHandler")
if "SetCacheEntryCommandHandler" in globals():
    globals()["SetCacheEntryHandler"] = globals()["SetCacheEntryCommandHandler"]
    __all__.append("SetCacheEntryHandler")
if "GetCacheEntryQueryHandler" in globals():
    globals()["GetCacheEntryHandler"] = globals()["GetCacheEntryQueryHandler"]
    __all__.append("GetCacheEntryHandler")
if "DeleteCacheEntryCommandHandler" in globals():
    globals()["DeleteCacheEntryHandler"] = globals()["DeleteCacheEntryCommandHandler"]
    __all__.append("DeleteCacheEntryHandler")
