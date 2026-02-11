"""Capability adapter backed by manifest + enabled modules."""

from __future__ import annotations

from sackmesser.domain.core.models import Capability
from sackmesser.domain.ports.core_ports import CapabilityPort
from sackmesser.infrastructure.runtime.modules import ModuleMetadata


class ManifestCapabilityProvider(CapabilityPort):
    """Expose capabilities declared in template manifest."""

    def __init__(
        self,
        *,
        manifest: dict[str, ModuleMetadata],
        enabled_modules: frozenset[str],
    ) -> None:
        self._manifest = manifest
        self._enabled_modules = enabled_modules

    async def list_capabilities(self) -> list[Capability]:
        capabilities: list[Capability] = []
        for name in sorted(self._manifest):
            module = self._manifest[name]
            capabilities.append(
                Capability(
                    name=name,
                    enabled=name in self._enabled_modules,
                    description=module.description,
                    resources=module.resources,
                )
            )
        return capabilities
