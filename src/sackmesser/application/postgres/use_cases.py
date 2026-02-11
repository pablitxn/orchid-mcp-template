"""Backward-compatible aliases for legacy workflow use-case names."""

from sackmesser.application.workflows.handlers import (
    CreateWorkflowUseCase,
    ListWorkflowsUseCase,
)

__all__ = ["CreateWorkflowUseCase", "ListWorkflowsUseCase"]
