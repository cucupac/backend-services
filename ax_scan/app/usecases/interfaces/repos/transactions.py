from abc import ABC, abstractmethod
from typing import Optional, List

from app.usecases.schemas.cross_chain_transaction import (
    CrossChainTransaction,
    UpdateCrossChainTransaction,
)
from app.usecases.schemas.evm_transaction import (
    EvmTransaction,
    EvmTransactionInDb,
    UpdateEvmTransaction,
)

from app.usecases.schemas.cross_chain_transaction import CrossChainTxJoinEvmTx


class ITransactionsRepo(ABC):
    @abstractmethod
    async def create_evm_tx(self, evm_tx: EvmTransaction) -> Optional[int]:
        """Inserts an evm transaction; returns evm_transaction id."""

    @abstractmethod
    async def create_cross_chain_tx(self, cross_chain_tx: CrossChainTransaction) -> int:
        """Inserts a cross-chain transaction; returns cross_chain_transaction id."""

    @abstractmethod
    async def update_cross_chain_tx(
        self,
        cross_chain_tx_id: int,
        update_values: UpdateCrossChainTransaction,
    ) -> None:
        """Updates a cross-chain transaction."""

    @abstractmethod
    async def retrieve_cross_chain_tx(
        self,
        chain_id: int,
        src_tx_hash: str,
    ) -> Optional[CrossChainTxJoinEvmTx]:
        """Returns a cross-chain transaction by chain ID and source-chain transaction hash."""

    @abstractmethod
    async def retrieve_pending(
        self,
        chain_id: int,
    ) -> List[EvmTransactionInDb]:
        """Retrieves pending evm transactions by chain ID."""

    @abstractmethod
    async def update_evm_tx(
        self,
        evm_tx_id: int,
        update_values: UpdateEvmTransaction,
    ) -> None:
        """Updates evm transactions by chain ID."""
