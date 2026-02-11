"""Unit tests for Redis API routes."""

from __future__ import annotations

from typing import Any

import pytest

from sackmesser.adapters.api.routes.redis import delete_cache, get_cache, set_cache
from sackmesser.adapters.api.schemas import SetCacheRequest
from sackmesser.application.errors import DisabledModuleError, NotFoundError
from sackmesser.application.requests.cache import (
    CacheEntryDto,
    DeleteCacheEntryCommand,
    DeleteCacheEntryResult,
    GetCacheEntryQuery,
    GetCacheEntryResult,
    SetCacheEntryCommand,
    SetCacheEntryResult,
)


class _FakeCommandBus:
    def __init__(self) -> None:
        self.calls: list[Any] = []

    async def dispatch(
        self,
        command: SetCacheEntryCommand | DeleteCacheEntryCommand,
    ) -> SetCacheEntryResult | DeleteCacheEntryResult:
        self.calls.append(command)
        if isinstance(command, SetCacheEntryCommand):
            return SetCacheEntryResult(success=True, key=command.key)
        if isinstance(command, DeleteCacheEntryCommand):
            return DeleteCacheEntryResult(success=True, key=command.key)
        msg = f"Unexpected command: {type(command)!r}"
        raise AssertionError(msg)


class _FakeQueryBus:
    def __init__(self, *, found: bool) -> None:
        self.found = found
        self.calls: list[Any] = []

    async def dispatch(self, query: GetCacheEntryQuery) -> GetCacheEntryResult:
        self.calls.append(query)
        return GetCacheEntryResult(
            entry=CacheEntryDto(
                key=query.key,
                value="1" if self.found else None,
                found=self.found,
            )
        )


class _Container:
    def __init__(self, enabled_modules: set[str], *, found: bool = True) -> None:
        self.enabled_modules = enabled_modules
        self.command_bus = _FakeCommandBus()
        self.query_bus = _FakeQueryBus(found=found)


async def test_set_cache_route_dispatches_command() -> None:
    container = _Container(enabled_modules={"core", "redis"})
    body = SetCacheRequest(value="1", ttl_seconds=60)

    payload = await set_cache(body, container, key="alpha")

    assert payload == {"success": True, "key": "alpha"}
    command = container.command_bus.calls[0]
    assert isinstance(command, SetCacheEntryCommand)
    assert command.ttl_seconds == 60


async def test_set_cache_route_raises_if_module_disabled() -> None:
    container = _Container(enabled_modules={"core"})
    body = SetCacheRequest(value="1")

    with pytest.raises(DisabledModuleError) as exc_info:
        await set_cache(body, container, key="alpha")

    assert exc_info.value.code == "module_disabled"


async def test_get_cache_route_returns_payload() -> None:
    container = _Container(enabled_modules={"core", "redis"}, found=True)

    payload = await get_cache(container, key="alpha")

    assert payload["entry"]["found"] is True
    query = container.query_bus.calls[0]
    assert isinstance(query, GetCacheEntryQuery)
    assert query.key == "alpha"


async def test_get_cache_route_raises_not_found() -> None:
    container = _Container(enabled_modules={"core", "redis"}, found=False)

    with pytest.raises(NotFoundError) as exc_info:
        await get_cache(container, key="missing")

    assert exc_info.value.code == "cache_not_found"
    assert exc_info.value.details["key"] == "missing"


async def test_get_cache_route_raises_if_module_disabled() -> None:
    container = _Container(enabled_modules={"core"})

    with pytest.raises(DisabledModuleError) as exc_info:
        await get_cache(container, key="alpha")

    assert exc_info.value.code == "module_disabled"


async def test_delete_cache_route_dispatches_command() -> None:
    container = _Container(enabled_modules={"core", "redis"})

    payload = await delete_cache(container, key="alpha")

    assert payload == {"success": True, "key": "alpha"}
    command = container.command_bus.calls[0]
    assert isinstance(command, DeleteCacheEntryCommand)
    assert command.key == "alpha"


async def test_delete_cache_route_raises_if_module_disabled() -> None:
    container = _Container(enabled_modules={"core"})

    with pytest.raises(DisabledModuleError) as exc_info:
        await delete_cache(container, key="alpha")

    assert exc_info.value.code == "module_disabled"
