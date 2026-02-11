"""CQRS message marker protocols."""

from __future__ import annotations

from typing import Protocol


class Command(Protocol):
    """Marker protocol for state-changing requests."""


class Query(Protocol):
    """Marker protocol for read-only requests."""
