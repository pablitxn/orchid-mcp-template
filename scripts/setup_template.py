#!/usr/bin/env python3
"""Interactive setup script for selecting/removing template modules.

This script reads `template/module-manifest.json`, asks which optional modules
should be enabled, resolves dependencies, writes `config/enabled_modules.json`,
and can optionally remove paths for disabled modules.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

MANIFEST_PATH = Path("template/module-manifest.json")
ENABLED_MODULES_PATH = Path("config/enabled_modules.json")


@dataclass(frozen=True, slots=True)
class ModuleDefinition:
    name: str
    required: bool
    description: str
    depends_on: tuple[str, ...]
    prune_paths: tuple[str, ...]


def load_manifest(path: Path) -> dict[str, ModuleDefinition]:
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))
    modules = raw.get("modules")
    if not isinstance(modules, dict) or not modules:
        raise ValueError("Invalid manifest: missing non-empty 'modules' object")

    parsed: dict[str, ModuleDefinition] = {}
    for module_name, payload in modules.items():
        if not isinstance(payload, dict):
            raise ValueError(f"Invalid manifest entry for module: {module_name}")

        parsed[module_name] = ModuleDefinition(
            name=module_name,
            required=bool(payload.get("required", False)),
            description=str(payload.get("description", "")),
            depends_on=tuple(payload.get("depends_on", [])),
            prune_paths=tuple(payload.get("prune_paths", [])),
        )

    for module in parsed.values():
        for dependency in module.depends_on:
            if dependency not in parsed:
                raise ValueError(
                    f"Module '{module.name}' depends on unknown module '{dependency}'"
                )

    return parsed


def parse_modules_argument(raw: str | None, available: set[str]) -> set[str]:
    if raw is None:
        return set()
    selected = {token.strip() for token in raw.split(",") if token.strip()}
    unknown = selected - available
    if unknown:
        unknown_list = ", ".join(sorted(unknown))
        raise ValueError(f"Unknown modules in --modules: {unknown_list}")
    return selected


def resolve_dependencies(
    selected: set[str], definitions: dict[str, ModuleDefinition]
) -> set[str]:
    resolved = set(selected)
    changed = True
    while changed:
        changed = False
        for module_name in list(resolved):
            for dep in definitions[module_name].depends_on:
                if dep not in resolved:
                    resolved.add(dep)
                    changed = True
    return resolved


def interactive_select(definitions: dict[str, ModuleDefinition]) -> set[str]:
    selected = {
        name
        for name, module in definitions.items()
        if module.required
    }
    optional = [name for name, module in definitions.items() if not module.required]

    print("Template setup: seleccion de modulos opcionales")
    for module_name in sorted(optional):
        module = definitions[module_name]
        prompt = f"Enable '{module_name}'? [y/N]: "
        answer = input(prompt).strip().lower()
        if answer in {"y", "yes", "s", "si"}:
            selected.add(module_name)
            print(f"  + {module_name}: {module.description}")
        else:
            print(f"  - {module_name}")

    return selected


def remove_path(path: Path, *, dry_run: bool) -> str:
    if not path.exists():
        return f"skip (missing): {path}"
    if dry_run:
        return f"would remove: {path}"
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
    return f"removed: {path}"


def prune_disabled_modules(
    disabled_modules: set[str],
    definitions: dict[str, ModuleDefinition],
    *,
    dry_run: bool,
) -> list[str]:
    actions: list[str] = []
    for module_name in sorted(disabled_modules):
        for raw_path in definitions[module_name].prune_paths:
            target = Path(raw_path)
            actions.append(remove_path(target, dry_run=dry_run))
    return actions


def write_enabled_modules(enabled: set[str], output_path: Path, *, dry_run: bool) -> None:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "enabled_modules": sorted(enabled),
    }

    if dry_run:
        print(f"[dry-run] would write {output_path}:")
        print(json.dumps(payload, indent=2))
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote: {output_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Select template modules and optionally prune disabled modules.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=MANIFEST_PATH,
        help=f"Path to module manifest (default: {MANIFEST_PATH})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ENABLED_MODULES_PATH,
        help=f"Path to enabled modules file (default: {ENABLED_MODULES_PATH})",
    )
    parser.add_argument(
        "--modules",
        type=str,
        default=None,
        help="Comma-separated modules to enable (optional modules only, required modules are always included).",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Remove declared paths for disabled modules.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing/deleting files.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    definitions = load_manifest(args.manifest)
    all_modules = set(definitions)
    required_modules = {name for name, module in definitions.items() if module.required}

    try:
        selected_by_flag = parse_modules_argument(args.modules, all_modules)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.modules is None:
        selected = interactive_select(definitions)
    else:
        selected = required_modules | selected_by_flag

    enabled = resolve_dependencies(selected, definitions)
    disabled = all_modules - enabled

    print("")
    print("Enabled modules:")
    for module_name in sorted(enabled):
        print(f"  - {module_name}")

    print("")
    print("Disabled modules:")
    for module_name in sorted(disabled):
        print(f"  - {module_name}")

    print("")
    write_enabled_modules(enabled, args.output, dry_run=args.dry_run)

    if args.prune:
        print("")
        print("Prune actions:")
        for action in prune_disabled_modules(disabled, definitions, dry_run=args.dry_run):
            print(f"  - {action}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
