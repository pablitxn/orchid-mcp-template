"""CQRS handler contracts."""

from __future__ import annotations

from typing import Protocol, TypeVar

from sackmesser.application.cqrs.messages import Command, Query

CommandT = TypeVar("CommandT", bound=Command, contravariant=True)
QueryT = TypeVar("QueryT", bound=Query, contravariant=True)
ResultT = TypeVar("ResultT", covariant=True)


class CommandHandler(Protocol[CommandT, ResultT]):
    """Handler contract for command messages."""

    async def handle(self, command: CommandT) -> ResultT:
        """Execute command and return result DTO."""


class QueryHandler(Protocol[QueryT, ResultT]):
    """Handler contract for query messages."""

    async def handle(self, query: QueryT) -> ResultT:
        """Execute query and return result DTO."""
