"""Use-case protocol and base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Protocol, TypeVar

from pydantic import BaseModel

RequestT = TypeVar("RequestT", bound=BaseModel, contravariant=True)
ResultT = TypeVar("ResultT", covariant=True)


class UseCase(Protocol[RequestT, ResultT]):
    """Generic contract for application use cases."""

    async def execute(self, request: RequestT) -> ResultT:
        """Execute the use case and return a response model."""


class BaseUseCase(ABC, Generic[RequestT, ResultT]):
    """Base class for typed use cases."""

    @abstractmethod
    async def execute(self, request: RequestT) -> ResultT:
        """Execute the use case and return a response model."""
