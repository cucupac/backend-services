from abc import ABC, abstractmethod


class IUniqueSetClient(ABC):
    @abstractmethod
    async def start_consumption(self) -> None:
        """Consumes messages from unique set."""

    @abstractmethod
    async def start(self) -> None:
        """Adds consumption loop to event loop."""
