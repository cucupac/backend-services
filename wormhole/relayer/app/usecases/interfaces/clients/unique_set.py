from abc import ABC, abstractmethod
from asyncio import AbstractEventLoop


class IUniqueSetClient(ABC):
    @abstractmethod
    async def start_consumption(self) -> None:
        """Consumes messages from unique set."""

    @abstractmethod
    async def start(self, loop: AbstractEventLoop) -> None:
        """Adds consumption loop to event loop."""
