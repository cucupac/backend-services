from abc import ABC, abstractmethod
from typing import Optional

from web3.types import TxReceipt, Nonce

from app.usecases.schemas.blockchain import TransactionHash


class IEvmClient(ABC):
    @abstractmethod
    async def deliver(
        self, payload: str, nonce: Optional[int] = None
    ) -> TransactionHash:
        """Sends transaction to the destination blockchain."""

    @abstractmethod
    async def fetch_receipt(self, transaction_hash: str) -> TxReceipt:
        """Fetches the transaction receipt for a given transaction hash."""

    @abstractmethod
    async def get_current_nonce(self) -> Nonce:
        """Retrieves the current nonce of the relayer on a provided destination chain."""
