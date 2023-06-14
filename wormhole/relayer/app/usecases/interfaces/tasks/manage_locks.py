from abc import ABC, abstractmethod


class IManageLocksTask(ABC):
    @abstractmethod
    async def start_task(self) -> None:
        """Starts task."""

    @abstractmethod
    async def task(self) -> None:
        """Removes stale locks if they exist."""
