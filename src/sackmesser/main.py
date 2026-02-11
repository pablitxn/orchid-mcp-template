"""Service entrypoint for API or MCP mode."""

from __future__ import annotations

import argparse
import asyncio

import uvicorn
from orchid_commons import load_config

from sackmesser.adapters.mcp import run_mcp_server
from sackmesser.infrastructure.runtime.state import resolve_environment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Orchid skills template service")
    parser.add_argument(
        "--mcp",
        action="store_true",
        help="Run MCP server on stdio instead of HTTP API",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable uvicorn autoreload in API mode",
    )
    return parser


def run_api(reload: bool) -> None:
    environment = resolve_environment()
    settings = load_config(config_dir="config", env=environment)
    uvicorn.run(
        "sackmesser.adapters.api.main:app",
        host=settings.service.host,
        port=settings.service.port,
        reload=reload,
    )


def main() -> None:
    args = build_parser().parse_args()
    if args.mcp:
        asyncio.run(run_mcp_server())
        return
    run_api(reload=args.reload)


if __name__ == "__main__":
    main()
