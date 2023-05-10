from abc import ABC, abstractmethod


class IGatherMissedVaasTask(ABC):
    @abstractmethod
    async def start_task(self) -> None:
        """Starts task."""

    @abstractmethod
    async def task(self):
        """Gathers untracked transactions."""
