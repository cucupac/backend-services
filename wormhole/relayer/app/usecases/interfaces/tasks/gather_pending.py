from abc import ABC, abstractmethod


class IGatherPendingVaasTask(ABC):
    @abstractmethod
    async def start_task(self) -> None:
        """Starts task."""
