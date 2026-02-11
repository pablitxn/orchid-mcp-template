"""Core application queries."""

from pydantic import BaseModel, ConfigDict, Field


class GetHealthQuery(BaseModel):
    """Request health data for runtime resources."""

    model_config = ConfigDict(frozen=True)

    include_optional_checks: bool = Field(default=True)


class GetCapabilitiesQuery(BaseModel):
    """Request currently available/active capabilities."""

    model_config = ConfigDict(frozen=True)
