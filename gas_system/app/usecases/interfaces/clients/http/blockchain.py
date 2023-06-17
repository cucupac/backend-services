from abc import ABC, abstractmethod

from app.usecases.schemas.blockchain import ComputeCosts, TransactionHash
from app.usecases.schemas.fees import MinimumFees
from app.usecases.schemas.evm import GasPrices


class IBlockchainClient(ABC):
    @abstractmethod
    async def update_fees(self, remote_data: MinimumFees) -> TransactionHash:
        """Sends transaction to the blockchain."""

    @abstractmethod
    async def estimate_fees(self) -> ComputeCosts:
        """Estimates a transaction's gas information."""

    @abstractmethod
    async def get_gas_prices(self, block_count: int) -> GasPrices:
        """Returns gas prices over specified number of recent blocks."""
