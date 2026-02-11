"""Unit tests for module manifest helpers."""

from sackmesser.infrastructure.runtime.modules import (
    ModuleMetadata,
    required_resource_names,
    resolve_enabled_modules,
)


def test_resolve_enabled_modules_includes_required() -> None:
    manifest = {
        "core": ModuleMetadata(
            name="core",
            description="base",
            required=True,
            resources=(),
        ),
        "postgres": ModuleMetadata(
            name="postgres",
            description="db",
            required=False,
            resources=("postgres",),
        ),
    }

    resolved = resolve_enabled_modules({"postgres"}, manifest)
    assert "core" in resolved
    assert "postgres" in resolved


def test_required_resources_from_modules() -> None:
    resources = required_resource_names(frozenset({"core", "postgres", "redis"}))
    assert resources == ["postgres", "redis"]
