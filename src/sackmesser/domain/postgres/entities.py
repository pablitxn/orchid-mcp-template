"""Domain entities for Postgres-backed examples."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Workflow:
    """A simple aggregate persisted in Postgres."""

    id: str
    title: str
    payload: dict[str, Any]
    created_at: datetime
