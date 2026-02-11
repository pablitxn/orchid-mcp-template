"""Core hexagonal ports."""

from __future__ import annotations

from typing import Protocol

from sackmesser.domain.core.models import Capability, HealthSnapshot


class CapabilityPort(Protocol):
    """Provides capability metadata from runtime/module config."""

    async def list_capabilities(self) -> list[Capability]:
        """Return all known capabilities."""


class HealthPort(Protocol):
    """Provides normalized health snapshots."""

    async def get_health(self) -> HealthSnapshot:
        """Return service health data."""
