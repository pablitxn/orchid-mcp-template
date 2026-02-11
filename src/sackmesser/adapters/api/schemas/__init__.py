"""API request/response schemas."""

from importlib import import_module

__all__: list[str] = []

_OPTIONAL_EXPORTS: dict[str, tuple[str, ...]] = {
    "sackmesser.adapters.api.schemas.postgres": ("CreateWorkflowRequest",),
    "sackmesser.adapters.api.schemas.redis": ("SetCacheRequest",),
}

for module_name, export_names in _OPTIONAL_EXPORTS.items():
    try:
        module = import_module(module_name)
    except ModuleNotFoundError:
        continue
    for export_name in export_names:
        globals()[export_name] = getattr(module, export_name)
    __all__.extend(export_names)
