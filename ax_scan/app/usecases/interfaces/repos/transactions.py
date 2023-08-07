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


class ITransactionsRepo(ABC):
    @abstractmethod
    async def create_evm_tx(self, evm_tx: EvmTransaction) -> int:
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
    async def retrieve_last_transaction(
        self,
        chain_id: int,
    ) -> Optional[EvmTransactionInDb]:
        """Retrieves last-stored transactions by chain_id."""

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
