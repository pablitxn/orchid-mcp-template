"""Unit tests for dynamic MCP tool registry."""

from __future__ import annotations

from types import SimpleNamespace

from sackmesser.adapters.mcp.tools import ToolSpec, load_tool_specs


async def _dummy_handler(_: object, __: dict[str, object]) -> dict[str, object]:
    return {}


def test_load_tool_specs_is_sorted_and_ignores_unknown(monkeypatch) -> None:
    captured_paths: list[str] = []
    alpha_specs = [
        ToolSpec(
            name="alpha_tool",
            description="alpha",
            input_schema={},
            handler=_dummy_handler,
        )
    ]
    beta_specs = [
        ToolSpec(
            name="beta_tool",
            description="beta",
            input_schema={},
            handler=_dummy_handler,
        )
    ]
    fake_modules: dict[str, object] = {
        "pkg.alpha": SimpleNamespace(get_tool_specs=lambda: alpha_specs),
        "pkg.beta": SimpleNamespace(get_tool_specs=lambda: beta_specs),
        "pkg.noget": SimpleNamespace(),
    }

    def fake_import_module(path: str) -> object:
        captured_paths.append(path)
        return fake_modules[path]

    monkeypatch.setattr(
        "sackmesser.adapters.mcp.tools.TOOL_MODULES",
        {
            "alpha": "pkg.alpha",
            "beta": "pkg.beta",
            "noget": "pkg.noget",
        },
    )
    monkeypatch.setattr("sackmesser.adapters.mcp.tools.import_module", fake_import_module)

    specs = load_tool_specs(["beta", "alpha", "beta", "unknown", "noget"])

    assert [spec.name for spec in specs] == ["alpha_tool", "beta_tool"]
    assert captured_paths == ["pkg.alpha", "pkg.beta", "pkg.noget"]
