from abc import ABC, abstractmethod

from app.usecases.schemas.cross_chain_transaction import (
    CrossChainTransaction,
    UpdateCrossChainTransaction,
)
from app.usecases.schemas.evm_transaction import EvmTransaction


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
        id: int,
        update_values: UpdateCrossChainTransaction,
    ) -> None:
        """Updates a cross-chain transaction."""
