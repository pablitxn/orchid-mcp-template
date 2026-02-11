"""Application use-case exports."""

from importlib import import_module

from sackmesser.application.use_cases.base import BaseUseCase, UseCase
from sackmesser.application.use_cases.core import GetCapabilitiesUseCase, GetHealthUseCase

__all__ = [
    "BaseUseCase",
    "GetCapabilitiesUseCase",
    "GetHealthUseCase",
    "UseCase",
]

_OPTIONAL_EXPORTS: dict[str, tuple[str, ...]] = {
    "sackmesser.application.use_cases.workflows": (
        "CreateWorkflowUseCase",
        "ListWorkflowsUseCase",
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
