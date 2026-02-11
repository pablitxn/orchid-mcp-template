"""Core API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from sackmesser.adapters.dependencies import ContainerDep
from sackmesser.application.requests.core import GetCapabilitiesQuery, GetHealthQuery

router = APIRouter()


@router.get("/health")
async def health(container: ContainerDep) -> dict[str, Any]:
    """Aggregated runtime health from commons ResourceManager."""
    result = await container.query_bus.dispatch(GetHealthQuery())
    return result.payload


@router.get("/api/v1/capabilities")
async def capabilities(container: ContainerDep) -> dict[str, Any]:
    """List available and enabled template capabilities."""
    result = await container.query_bus.dispatch(GetCapabilitiesQuery())
    return result.model_dump()
