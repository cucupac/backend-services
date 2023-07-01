from abc import ABC, abstractmethod
from typing import List, Mapping

from app.usecases.schemas.blockchain import ComputeCosts


class IRemotePriceManager(ABC):
    @abstractmethod
    async def update_remote_fees(self, chains_to_update: List[int]) -> None:
        """Updates gas prices for remote computation in local native token."""

    @abstractmethod
    async def add_buffer(
        self, remote_chain_id: int, remote_fee_in_local_native: int
    ) -> int:
        """Adds buffer to remote fee."""

    @abstractmethod
    async def get_chain_compute_costs(self) -> Mapping[int, ComputeCosts]:
        """Returns the cost of delivery data on all chains."""

    @abstractmethod
    async def get_remote_fees(
        self, compute_costs: Mapping[int, ComputeCosts], chains_to_update: List[int]
    ) -> Mapping[int, Mapping[int, int]]:
        """Returns a dictionary of fee updates, in terms of source chain native currency, for each source chain."""
