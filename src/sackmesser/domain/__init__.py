"""Domain layer for strict hexagonal template."""

from importlib import import_module

from sackmesser.domain.core import Capability, HealthSnapshot

__all__ = [
    "Capability",
    "HealthSnapshot",
]

_OPTIONAL_EXPORTS: dict[str, tuple[str, ...]] = {
    "sackmesser.domain.workflows": ("Workflow",),
    "sackmesser.domain.cache": ("CacheEntry",),
}

for module_name, export_names in _OPTIONAL_EXPORTS.items():
    try:
        module = import_module(module_name)
    except ModuleNotFoundError:
        continue
    for export_name in export_names:
        globals()[export_name] = getattr(module, export_name)
    __all__.extend(export_names)
