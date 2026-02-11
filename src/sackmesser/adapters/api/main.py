"""FastAPI app factory."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from orchid_commons import create_fastapi_observability_middleware, load_config

from sackmesser.adapters.api.routes import load_routers
from sackmesser.adapters.dependencies import init_services, shutdown_services
from sackmesser.infrastructure.runtime.modules import (
    load_enabled_modules,
    load_module_manifest,
    resolve_enabled_modules,
)
from sackmesser.infrastructure.runtime.state import resolve_environment


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize runtime resources on startup and close them on shutdown."""
    await init_services()
    yield
    await shutdown_services()


def create_app() -> FastAPI:
    """Create configured FastAPI application."""
    environment = resolve_environment()
    settings = load_config(config_dir="config", env=environment)

    app = FastAPI(
        title=settings.service.name,
        version=settings.service.version,
        description="Orchid skills template with strict hexagonal modules",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(create_fastapi_observability_middleware())

    manifest = load_module_manifest()
    enabled_modules = resolve_enabled_modules(load_enabled_modules(), manifest)
    for router in load_routers(enabled_modules):
        app.include_router(router)

    return app


app = create_app()
