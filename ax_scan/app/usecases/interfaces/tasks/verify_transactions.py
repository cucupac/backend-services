from abc import ABC, abstractmethod


class IVerifyTransactionsTask(ABC):
    @abstractmethod
    async def start_task(self) -> None:
        """Starts task."""

    @abstractmethod
    async def task(self, task_id: int) -> None:
        """Gathers untracked transactions."""
