from abc import ABC, abstractmethod
from typing import Optional

from web3.types import TxReceipt

from app.usecases.schemas.blockchain import TransactionHash


class IEvmClient(ABC):
    @abstractmethod
    async def deliver(
        self, payload: str, dest_chain_id: int, nonce: Optional[int]
    ) -> TransactionHash:
        """Sends transaction to the destination blockchain."""

    @abstractmethod
    async def fetch_receipt(
        self, transaction_hash: str, dest_chain_id: int
    ) -> TxReceipt:
        """Fetches the transaction receipt for a given transaction hash."""

    @abstractmethod
    async def get_current_nonce(self, dest_chain_id: int) -> int:
        """Retrieves the current nonce of the relayer on a provided destination chain."""
