"""Unit tests for setup template script helpers."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest


def _load_setup_template_module() -> ModuleType:
    root = Path(__file__).resolve().parents[3]
    module_path = root / "scripts" / "setup_template.py"
    spec = importlib.util.spec_from_file_location("setup_template_for_tests", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


setup_template = _load_setup_template_module()


def test_parse_modules_argument_none_returns_empty_set() -> None:
    selected = setup_template.parse_modules_argument(None, {"core", "postgres", "redis"})
    assert selected == set()


def test_parse_modules_argument_unknown_module_raises() -> None:
    with pytest.raises(ValueError, match="Unknown modules in --modules: nope"):
        setup_template.parse_modules_argument("core,nope", {"core", "postgres", "redis"})


def test_resolve_dependencies_adds_required_modules() -> None:
    definitions = {
        "core": setup_template.ModuleDefinition(
            name="core",
            required=True,
            description="base",
            depends_on=(),
            prune_paths=(),
        ),
        "postgres": setup_template.ModuleDefinition(
            name="postgres",
            required=False,
            description="db",
            depends_on=("core",),
            prune_paths=(),
        ),
        "redis": setup_template.ModuleDefinition(
            name="redis",
            required=False,
            description="cache",
            depends_on=("core",),
            prune_paths=(),
        ),
    }

    resolved = setup_template.resolve_dependencies({"postgres", "redis"}, definitions)
    assert resolved == {"core", "postgres", "redis"}


def test_sync_appsettings_resources_filters_managed_keys(tmp_path: Path) -> None:
    appsettings_path = tmp_path / "appsettings.json"
    appsettings_path.write_text(
        json.dumps(
            {
                "service": {"name": "demo"},
                "resources": {
                    "postgres": {"dsn": "postgres://"},
                    "redis": {"url": "redis://"},
                    "custom": {"enabled": True},
                },
            }
        ),
        encoding="utf-8",
    )

    setup_template.sync_appsettings_resources(
        {"core", "postgres"},
        appsettings_path=appsettings_path,
        dry_run=False,
    )

    payload = json.loads(appsettings_path.read_text(encoding="utf-8"))
    assert set(payload["resources"]) == {"custom", "postgres"}
    assert payload["resources"]["custom"]["enabled"] is True


def test_build_docker_compose_for_core_only_has_empty_services() -> None:
    content = setup_template.build_docker_compose({"core"})
    assert "services: {}" in content
    assert "volumes: {}" in content


def test_prune_disabled_modules_dry_run_does_not_delete(tmp_path: Path) -> None:
    target = tmp_path / "to_prune.txt"
    target.write_text("demo", encoding="utf-8")
    definitions = {
        "redis": setup_template.ModuleDefinition(
            name="redis",
            required=False,
            description="cache",
            depends_on=("core",),
            prune_paths=(str(target),),
        )
    }

    actions = setup_template.prune_disabled_modules(
        {"redis"},
        definitions,
        dry_run=True,
    )

    assert actions == [f"would remove: {target}"]
    assert target.exists()
