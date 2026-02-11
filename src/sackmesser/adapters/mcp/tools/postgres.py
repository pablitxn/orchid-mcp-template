"""Postgres MCP tools."""

from __future__ import annotations

from typing import Any

from sackmesser.adapters.mcp.errors import MCPToolError
from sackmesser.application.workflows import CreateWorkflowCommand, ListWorkflowsQuery
from sackmesser.infrastructure.runtime.container import ApplicationContainer

from .common import ToolSpec


async def create_workflow_tool(
    container: ApplicationContainer,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Create a Postgres workflow."""
    if "postgres" not in container.enabled_modules:
        raise MCPToolError(
            code="module_disabled",
            message="Module 'postgres' is disabled",
            details={"module": "postgres"},
        )

    command = CreateWorkflowCommand(
        title=arguments["title"],
        payload=arguments.get("payload", {}),
    )
    return (await container.command_bus.dispatch(command)).model_dump()


async def list_workflows_tool(
    container: ApplicationContainer,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """List Postgres workflows."""
    if "postgres" not in container.enabled_modules:
        raise MCPToolError(
            code="module_disabled",
            message="Module 'postgres' is disabled",
            details={"module": "postgres"},
        )

    query = ListWorkflowsQuery(
        limit=arguments.get("limit", 20),
        offset=arguments.get("offset", 0),
    )
    return (await container.query_bus.dispatch(query)).model_dump()


def get_tool_specs() -> list[ToolSpec]:
    """Return MCP tool specs for postgres module."""
    return [
        ToolSpec(
            name="create_workflow",
            description="Create a workflow persisted in Postgres.",
            input_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "payload": {"type": "object"},
                },
                "required": ["title"],
            },
            handler=create_workflow_tool,
        ),
        ToolSpec(
            name="list_workflows",
            description="List workflows from Postgres.",
            input_schema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                    "offset": {"type": "integer", "minimum": 0},
                },
            },
            handler=list_workflows_tool,
        ),
    ]
