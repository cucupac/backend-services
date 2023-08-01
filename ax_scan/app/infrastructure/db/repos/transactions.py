from databases import Database

from app.infrastructure.db.models.cross_chain_transactions import (
    CROSS_CHAIN_TRANSACTIONS,
)
from app.infrastructure.db.models.evm_transactions import EVM_TRANSACTIONS
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.schemas.cross_chain_transaction import (
    CrossChainTransaction,
    UpdateCrossChainTransaction,
)
from app.usecases.schemas.evm_transaction import EvmTransaction


class TransactionsRepo(ITransactionsRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create_evm_tx(self, evm_tx: EvmTransaction) -> int:
        """Inserts an evm transaction; returns evm_transaction id."""

        chain_tx_insert_stmt = EVM_TRANSACTIONS.insert().values(
            chain_id=evm_tx.chain_id,
            transaction_hash=evm_tx.transaction_hash,
            block_hash=evm_tx.block_hash,
            block_number=evm_tx.block_number,
            status=evm_tx.status,
            gas_price=evm_tx.gas_price,
            gas_used=evm_tx.gas_used,
            timestamp=evm_tx.timestamp,
        )

        return await self.db.execute(chain_tx_insert_stmt)

    async def create_cross_chain_tx(self, cross_chain_tx: CrossChainTransaction) -> int:
        """Inserts a cross-chain transaction; returns cross_chain_transaction id."""

        cross_chain_tx_insert_stmt = CROSS_CHAIN_TRANSACTIONS.insert().values(
            bridge=cross_chain_tx.bridge,
            from_address=cross_chain_tx.from_address,
            to_address=cross_chain_tx.to_address,
            source_chain_id=cross_chain_tx.source_chain_id,
            dest_chain_id=cross_chain_tx.dest_chain_id,
            amount=cross_chain_tx.amount,
            source_chain_tx_id=cross_chain_tx.source_chain_tx_id,
            dest_chain_tx_id=cross_chain_tx.dest_chain_tx_id,
        )

        return await self.db.execute(cross_chain_tx_insert_stmt)

    async def update_cross_chain_tx(
        self,
        cross_chain_tx_id: int,
        update_values: UpdateCrossChainTransaction,
    ) -> None:
        """Updates a cross-chain transaction."""

        update_dict = {}
        for key, value in update_values.model_dump().items():
            if value is not None:
                update_dict[key] = value

        cross_chain_tx_update_stmt = (
            CROSS_CHAIN_TRANSACTIONS.update()
            .values(update_dict)
            .where(CROSS_CHAIN_TRANSACTIONS.c.id == cross_chain_tx_id)
        )

        await self.db.execute(cross_chain_tx_update_stmt)
