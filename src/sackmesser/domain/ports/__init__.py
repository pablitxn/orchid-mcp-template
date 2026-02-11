"""Domain ports."""

from importlib import import_module

from sackmesser.domain.ports.core_ports import CapabilityPort, HealthPort

__all__ = [
    "CapabilityPort",
    "HealthPort",
]

_OPTIONAL_EXPORTS: dict[str, tuple[str, ...]] = {
    "sackmesser.domain.ports.workflow_ports": ("WorkflowRepositoryPort",),
    "sackmesser.domain.ports.cache_ports": ("CacheRepositoryPort",),
}

for module_name, export_names in _OPTIONAL_EXPORTS.items():
    try:
        module = import_module(module_name)
    except ModuleNotFoundError:
        continue
    for export_name in export_names:
        globals()[export_name] = getattr(module, export_name)
    __all__.extend(export_names)
