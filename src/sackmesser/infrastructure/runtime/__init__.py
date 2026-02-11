"""Runtime bootstrap and module helpers."""

from sackmesser.infrastructure.runtime.container import ApplicationContainer
from sackmesser.infrastructure.runtime.modules import (
    ENABLED_MODULES_PATH,
    MODULE_MANIFEST_PATH,
    ModuleMetadata,
    load_enabled_modules,
    load_module_manifest,
    required_resource_names,
    resolve_enabled_modules,
)
from sackmesser.infrastructure.runtime.state import (
    RuntimeState,
    get_runtime_container,
    get_runtime_state,
    resolve_environment,
    reset_runtime_state_for_tests,
    shutdown_runtime,
    startup_runtime,
)

__all__ = [
    "ApplicationContainer",
    "ENABLED_MODULES_PATH",
    "MODULE_MANIFEST_PATH",
    "ModuleMetadata",
    "RuntimeState",
    "get_runtime_container",
    "get_runtime_state",
    "load_enabled_modules",
    "load_module_manifest",
    "required_resource_names",
    "resolve_enabled_modules",
    "resolve_environment",
    "reset_runtime_state_for_tests",
    "shutdown_runtime",
    "startup_runtime",
]
