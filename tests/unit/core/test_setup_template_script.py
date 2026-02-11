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
    assert payload["observability"]["enabled"] is False
    assert payload["observability"]["langfuse"]["enabled"] is False


def test_sync_appsettings_resources_adds_defaults_for_new_modules(tmp_path: Path) -> None:
    appsettings_path = tmp_path / "appsettings.json"
    appsettings_path.write_text(
        json.dumps(
            {
                "service": {"name": "demo"},
                "resources": {"custom": {"enabled": True}},
            }
        ),
        encoding="utf-8",
    )

    setup_template.sync_appsettings_resources(
        {"core", "blob", "mongodb"},
        appsettings_path=appsettings_path,
        dry_run=False,
    )

    payload = json.loads(appsettings_path.read_text(encoding="utf-8"))
    assert set(payload["resources"]) == {"custom", "minio", "mongodb", "multi_bucket", "r2"}
    assert payload["resources"]["minio"]["endpoint"] == "localhost:9000"
    assert payload["resources"]["mongodb"]["uri"] == "mongodb://localhost:27017"
    assert payload["resources"]["r2"] is None
    assert payload["resources"]["multi_bucket"] is None


def test_sync_appsettings_resources_keeps_observability_on_when_module_selected(
    tmp_path: Path,
) -> None:
    appsettings_path = tmp_path / "appsettings.json"
    appsettings_path.write_text(
        json.dumps(
            {
                "service": {"name": "demo"},
                "resources": {},
            }
        ),
        encoding="utf-8",
    )

    setup_template.sync_appsettings_resources(
        {"core", "observability"},
        appsettings_path=appsettings_path,
        dry_run=False,
    )

    payload = json.loads(appsettings_path.read_text(encoding="utf-8"))
    assert payload["observability"]["enabled"] is True
    assert payload["observability"]["langfuse"]["enabled"] is False


def test_build_docker_compose_for_core_only_has_empty_services() -> None:
    content = setup_template.build_docker_compose({"core"})
    assert "services: {}" in content
    assert "volumes: {}" in content


def test_build_docker_compose_for_full_stack_contains_extended_services() -> None:
    content = setup_template.build_docker_compose(
        {"core", "postgres", "redis", "mongodb", "qdrant", "rabbitmq", "blob"}
    )
    assert "  postgres:" in content
    assert "  redis:" in content
    assert "  mongodb:" in content
    assert "  qdrant:" in content
    assert "  rabbitmq:" in content
    assert "  minio:" in content
    assert "  mongodb_data:" in content
    assert "  qdrant_data:" in content
    assert "  rabbitmq_data:" in content
    assert "  minio_data:" in content


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


def test_load_manifest_rejects_absolute_prune_path(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "modules": {
                    "core": {"required": True, "depends_on": [], "prune_paths": []},
                    "redis": {
                        "required": False,
                        "depends_on": ["core"],
                        "prune_paths": ["/tmp/evil"],
                    },
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="absolute/invalid prune path"):
        setup_template.load_manifest(manifest_path)


def test_load_manifest_rejects_duplicate_prune_paths(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "modules": {
                    "core": {"required": True, "depends_on": [], "prune_paths": []},
                    "redis": {
                        "required": False,
                        "depends_on": ["core"],
                        "prune_paths": ["src/sackmesser/shared"],
                    },
                    "postgres": {
                        "required": False,
                        "depends_on": ["core"],
                        "prune_paths": ["src/sackmesser/shared"],
                    },
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate prune path"):
        setup_template.load_manifest(manifest_path)


def test_find_missing_optional_dependencies_by_module(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fake_find_spec(name: str) -> object | None:
        if name in {"asyncpg", "aio_pika"}:
            return None
        return object()

    monkeypatch.setattr(setup_template, "find_spec", _fake_find_spec)
    missing = setup_template.find_missing_optional_dependencies(
        {"core", "postgres", "rabbitmq", "redis"}
    )

    assert missing == {
        "postgres": ("asyncpg",),
        "rabbitmq": ("aio_pika",),
    }


def test_print_dependency_diagnostics_strict_returns_failure(capsys: pytest.CaptureFixture[str]) -> None:
    should_fail = setup_template.print_dependency_diagnostics(
        {"postgres": ("asyncpg",)},
        strict=True,
    )
    output = capsys.readouterr().out

    assert should_fail is True
    assert "install hint" in output
    assert "--extra db" in output
