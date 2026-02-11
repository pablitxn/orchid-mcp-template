"""E2E smoke tests for API with core module."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from sackmesser.adapters.api.main import create_app


@pytest.fixture
def core_only_enabled_modules(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "schema_version": 1,
        "enabled_modules": ["core"],
    }
    enabled_path = tmp_path / "enabled_modules.json"
    enabled_path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setenv("ORCHID_ENABLED_MODULES_PATH", str(enabled_path))


def test_health_endpoint(core_only_enabled_modules: None) -> None:
    del core_only_enabled_modules
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert "status" in payload


def test_capabilities_endpoint(core_only_enabled_modules: None) -> None:
    del core_only_enabled_modules
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/api/v1/capabilities")
    assert response.status_code == 200
    payload = response.json()
    assert "capabilities" in payload
    assert any(item["name"] == "core" for item in payload["capabilities"])
