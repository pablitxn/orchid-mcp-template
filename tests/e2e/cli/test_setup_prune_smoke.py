"""E2E smoke tests for real prune flow in a temporary repository copy."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
COPY_DIRS = ("src", "config", "template", "scripts")
COPY_FILES = ("docker-compose.yml",)


def _copy_minimal_repo(tmp_path: Path) -> Path:
    repo_path = tmp_path / "repo"
    repo_path.mkdir(parents=True, exist_ok=True)

    for directory in COPY_DIRS:
        shutil.copytree(PROJECT_ROOT / directory, repo_path / directory)
    for filename in COPY_FILES:
        shutil.copy2(PROJECT_ROOT / filename, repo_path / filename)
    return repo_path


def _run(cwd: Path, *args: str) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(cwd / "src")
    completed = subprocess.run(
        args,
        cwd=cwd,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        joined = " ".join(args)
        raise AssertionError(
            f"Command failed: {joined}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )


def test_setup_prune_core_only_keeps_api_and_mcp_importable(tmp_path: Path) -> None:
    repo_path = _copy_minimal_repo(tmp_path)

    _run(
        repo_path,
        sys.executable,
        "scripts/setup_template.py",
        "--modules",
        "core",
        "--prune",
    )
    _run(
        repo_path,
        sys.executable,
        "-c",
        "from sackmesser.adapters.api.main import create_app; create_app()",
    )
    _run(
        repo_path,
        sys.executable,
        "-c",
        (
            "import asyncio\n"
            "from sackmesser.adapters.mcp.server import create_mcp_server\n"
            "from sackmesser.infrastructure.runtime.state import shutdown_runtime, startup_runtime\n"
            "async def _main() -> None:\n"
            "    await startup_runtime()\n"
            "    create_mcp_server()\n"
            "    await shutdown_runtime()\n"
            "asyncio.run(_main())\n"
        ),
    )
