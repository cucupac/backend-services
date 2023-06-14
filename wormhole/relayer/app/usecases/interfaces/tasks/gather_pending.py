from abc import ABC, abstractmethod


class IGatherPendingVaasTask(ABC):
    @abstractmethod
    async def start_task(self) -> None:
        """Starts task."""

    @abstractmethod
    async def task(self, task_id: int) -> None:
        """Marks stale transactions as failed."""
