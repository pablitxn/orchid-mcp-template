"""Dynamic API router registry."""

from __future__ import annotations

from collections.abc import Iterable
from importlib import import_module

from fastapi import APIRouter

ROUTE_MODULES: dict[str, str] = {
    "core": "sackmesser.adapters.api.routes.core",
    "postgres": "sackmesser.adapters.api.routes.postgres",
    "redis": "sackmesser.adapters.api.routes.redis",
}


def load_routers(enabled_modules: Iterable[str]) -> list[APIRouter]:
    """Load routers only for enabled modules."""
    routers: list[APIRouter] = []
    for module_name in sorted(set(enabled_modules)):
        module_path = ROUTE_MODULES.get(module_name)
        if module_path is None:
            continue
        module = import_module(module_path)
        router = getattr(module, "router", None)
        if isinstance(router, APIRouter):
            routers.append(router)
    return routers


__all__ = ["load_routers"]
