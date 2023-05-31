from abc import ABC, abstractmethod


class IGatherPendingVaasTask(ABC):
    @abstractmethod
    async def start_task(self) -> None:
        """Starts task."""

    @abstractmethod
    async def task(self) -> None:
        """Marks stale transactions as failed."""
