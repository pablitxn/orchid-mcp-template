"""Minimal typed command/query buses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sackmesser.application.cqrs.handlers import CommandHandler, QueryHandler
from sackmesser.application.cqrs.messages import Command, Query


class HandlerNotRegisteredError(LookupError):
    """Raised when a message is dispatched without a registered handler."""

    def __init__(self, message_type: type[object]) -> None:
        super().__init__(f"No handler registered for message type: {message_type.__name__}")
        self.message_type = message_type


@dataclass(slots=True)
class CommandBus:
    """In-memory registry and dispatcher for command handlers."""

    _handlers: dict[type[object], CommandHandler[Any, Any]] = field(default_factory=dict)

    def register(
        self,
        command_type: type[Command],
        handler: CommandHandler[Any, Any],
    ) -> None:
        self._handlers[command_type] = handler

    def has_handler(self, command_type: type[Command]) -> bool:
        return command_type in self._handlers

    async def dispatch(self, command: Command) -> Any:
        handler = self._handlers.get(type(command))
        if handler is None:
            raise HandlerNotRegisteredError(type(command))
        return await handler.handle(command)


@dataclass(slots=True)
class QueryBus:
    """In-memory registry and dispatcher for query handlers."""

    _handlers: dict[type[object], QueryHandler[Any, Any]] = field(default_factory=dict)

    def register(
        self,
        query_type: type[Query],
        handler: QueryHandler[Any, Any],
    ) -> None:
        self._handlers[query_type] = handler

    def has_handler(self, query_type: type[Query]) -> bool:
        return query_type in self._handlers

    async def dispatch(self, query: Query) -> Any:
        handler = self._handlers.get(type(query))
        if handler is None:
            raise HandlerNotRegisteredError(type(query))
        return await handler.handle(query)
