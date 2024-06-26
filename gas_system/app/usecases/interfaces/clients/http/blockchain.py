from abc import ABC, abstractmethod

from app.usecases.schemas.blockchain import ComputeCosts, TransactionHash
from app.usecases.schemas.fees import MinimumFees


class IBlockchainClient(ABC):
    @abstractmethod
    async def update_fees(
        self, remote_data: MinimumFees, compute_costs: ComputeCosts
    ) -> TransactionHash:
        """Sends transaction to the blockchain."""

    @abstractmethod
    async def estimate_fees(self) -> ComputeCosts:
        """Estimates a transaction's gas information."""
