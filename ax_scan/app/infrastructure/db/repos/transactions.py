from typing import Optional, List

from databases import Database
from sqlalchemy import select, and_

from app.infrastructure.db.models.cross_chain_transactions import (
    CROSS_CHAIN_TRANSACTIONS,
)
from app.infrastructure.db.models.evm_transactions import EVM_TRANSACTIONS
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.schemas.cross_chain_transaction import (
    CrossChainTransaction,
    UpdateCrossChainTransaction,
    CrossChainTxJoinEvmTx,
    Status,
)
from app.usecases.schemas.evm_transaction import (
    EvmTransaction,
    EvmTransactionInDb,
    UpdateEvmTransaction,
    EvmTransactionStatus,
)


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
            error=evm_tx.error,
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

    async def retrieve_cross_chain_tx(
        self,
        chain_id: int,
        src_tx_hash: str,
    ) -> Optional[CrossChainTxJoinEvmTx]:
        """Returns a cross-chain transaction by chain ID and source-chain transaction hash."""

        j = CROSS_CHAIN_TRANSACTIONS.join(
            EVM_TRANSACTIONS,
            CROSS_CHAIN_TRANSACTIONS.c.source_chain_tx_id == EVM_TRANSACTIONS.c.id,
        )

        columns_to_select = [
            CROSS_CHAIN_TRANSACTIONS,
            EVM_TRANSACTIONS.c.status.label("source_chain_tx_status"),
        ]

        query = (
            select(columns_to_select)
            .select_from(j)
            .where(
                and_(
                    EVM_TRANSACTIONS.c.chain_id == chain_id,
                    EVM_TRANSACTIONS.c.transaction_hash == src_tx_hash,
                )
            )
        )

        async with self.db.transaction():
            cross_chain_tx_record = await self.db.fetch_one(query)

            if not cross_chain_tx_record:
                return

            if cross_chain_tx_record.dest_chain_tx_id:
                query = select([EVM_TRANSACTIONS]).where(
                    EVM_TRANSACTIONS.c.id == cross_chain_tx_record.dest_chain_tx_id
                )
                evm_tx = await self.db.fetch_one(query)
                dest_chain_tx = EvmTransactionInDb(**evm_tx)
                return CrossChainTxJoinEvmTx(
                    **cross_chain_tx_record, dest_chain_tx_status=dest_chain_tx.status
                )
            return CrossChainTxJoinEvmTx(
                **cross_chain_tx_record, dest_chain_tx_status=Status.PENDING
            )

    async def retrieve_last_transaction(
        self,
        chain_id: int,
    ) -> Optional[EvmTransactionInDb]:
        """Retrieves last-stored transaction by chain_id."""

        query = (
            select([EVM_TRANSACTIONS])
            .where(EVM_TRANSACTIONS.c.chain_id == chain_id)
            .order_by(EVM_TRANSACTIONS.c.block_number.desc())
            .limit(1)
        )

        result = await self.db.fetch_one(query)

        return EvmTransactionInDb(**result) if result else None

    async def retrieve_pending(
        self,
        chain_id: int,
    ) -> List[EvmTransactionInDb]:
        """Retrieves pending evm transactions by chain ID."""

        query = select([EVM_TRANSACTIONS]).where(
            and_(
                EVM_TRANSACTIONS.c.chain_id == chain_id,
                EVM_TRANSACTIONS.c.status == EvmTransactionStatus.PENDING,
            )
        )

        results = await self.db.fetch_all(query)

        return [EvmTransactionInDb(**result) for result in results]

    async def update_evm_tx(
        self,
        evm_tx_id: int,
        update_values: UpdateEvmTransaction,
    ) -> None:
        """Updates evm transactions by chain ID."""

        update_dict = {}
        for key, value in update_values.model_dump().items():
            if key == "error":
                update_dict[key] = value
            elif value is not None:
                update_dict[key] = value

        evm_tx_update_stmt = (
            EVM_TRANSACTIONS.update()
            .values(update_dict)
            .where(EVM_TRANSACTIONS.c.id == evm_tx_id)
        )

        await self.db.execute(evm_tx_update_stmt)
