from abc import ABC, abstractmethod


class IRemotePriceManager(ABC):
    @abstractmethod
    async def update_remote_fees(self) -> None:
        """Updates gas prices for remote computation in local native token."""
