from abc import ABC, abstractmethod


class IVerifyDeliveryTask(ABC):
    @abstractmethod
    async def start_task(self) -> None:
        """Starts task."""

    @abstractmethod
    async def task(self):
        """Verifies the delivery status of previously submitted transactions."""
