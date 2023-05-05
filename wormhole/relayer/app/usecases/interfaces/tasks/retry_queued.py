from abc import ABC, abstractmethod


class IRetryQueuedTask(ABC):
    @abstractmethod
    async def start_task(self) -> None:
        """Starts automated task to periodically update remote fees."""
