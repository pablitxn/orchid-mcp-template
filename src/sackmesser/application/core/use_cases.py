"""Backward-compatible aliases for legacy use-case names."""

from sackmesser.application.core.handlers import (
    GetCapabilitiesQueryHandler as GetCapabilitiesUseCase,
)
from sackmesser.application.core.handlers import GetHealthQueryHandler as GetHealthUseCase

__all__ = ["GetCapabilitiesUseCase", "GetHealthUseCase"]
