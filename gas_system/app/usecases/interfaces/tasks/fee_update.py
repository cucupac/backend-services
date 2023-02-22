from abc import ABC, abstractmethod


class IUpdateFeeTask(ABC):
    @abstractmethod
    async def start_task(self) -> None:
        """Starts automated task to periodically update remote fees."""
