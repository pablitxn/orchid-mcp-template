"""Postgres application queries."""

from pydantic import BaseModel, ConfigDict, Field


class ListWorkflowsQuery(BaseModel):
    """List workflows from Postgres."""

    model_config = ConfigDict(frozen=True)

    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
