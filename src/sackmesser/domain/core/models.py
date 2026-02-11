"""Core domain models shared by API and MCP adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Capability:
    """Represents a selectable module/capability in the template."""

    name: str
    enabled: bool
    description: str
    resources: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class HealthSnapshot:
    """Health data normalized for application use cases."""

    status: str
    payload: dict[str, Any]
