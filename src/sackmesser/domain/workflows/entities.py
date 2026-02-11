"""Domain entities for workflow capability."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Workflow:
    """Workflow aggregate root used by application handlers."""

    id: str
    title: str
    payload: dict[str, Any]
    created_at: datetime
