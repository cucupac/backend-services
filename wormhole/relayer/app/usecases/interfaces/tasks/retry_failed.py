from abc import ABC, abstractmethod


class IRetryFailedTask(ABC):
    @abstractmethod
    async def start_task(self) -> None:
        """Starts task."""
