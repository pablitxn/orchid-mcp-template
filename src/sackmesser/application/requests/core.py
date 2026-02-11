"""Core request/response models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GetHealthQuery(BaseModel):
    """Request health data for runtime resources."""

    model_config = ConfigDict(frozen=True)

    include_optional_checks: bool = Field(default=True)


class GetCapabilitiesQuery(BaseModel):
    """Request currently available/active capabilities."""

    model_config = ConfigDict(frozen=True)


class CapabilityDto(BaseModel):
    """Capability data for API/MCP outputs."""

    model_config = ConfigDict(frozen=True)

    name: str
    enabled: bool
    description: str
    resources: list[str]


class GetCapabilitiesResult(BaseModel):
    """Result for capability listing."""

    model_config = ConfigDict(frozen=True)

    capabilities: list[CapabilityDto]


class GetHealthResult(BaseModel):
    """Result for health endpoint/tool."""

    model_config = ConfigDict(frozen=True)

    status: str
    payload: dict[str, Any]
