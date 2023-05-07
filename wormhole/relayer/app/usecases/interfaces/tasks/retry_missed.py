from abc import ABC, abstractmethod


class IRetryMissedTask(ABC):
    @abstractmethod
    async def start_task(self) -> None:
        """Starts task."""
