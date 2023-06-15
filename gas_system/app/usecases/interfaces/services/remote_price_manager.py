from abc import ABC, abstractmethod
from typing import List


class IRemotePriceManager(ABC):
    @abstractmethod
    async def update_remote_fees(self, chains_to_update: List[int]) -> None:
        """Updates gas prices for remote computation in local native token."""
