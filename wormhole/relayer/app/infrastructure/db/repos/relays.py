from datetime import datetime, timedelta
from typing import List, Optional

from databases import Database
from sqlalchemy import and_, select

from app.infrastructure.db.models.relays import RELAYS
from app.infrastructure.db.models.transactions import TRANSACTIONS
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.schemas.relays import (
    CacheStatus,
    Status,
    UpdateJoinedRepoAdapter,
    UpdateRepoAdapter,
)
from app.usecases.schemas.transactions import CreateRepoAdapter, TransactionsJoinRelays


class RelaysRepo(IRelaysRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(self, transaction: CreateRepoAdapter) -> None:
        """Creates new transaction and relay object."""

        insert_statement = TRANSACTIONS.insert().values(
            emitter_address=transaction.emitter_address.lower(),
            from_address=transaction.from_address.lower(),
            to_address=transaction.to_address.lower(),
            source_chain_id=transaction.source_chain_id,
            dest_chain_id=transaction.dest_chain_id,
            amount=transaction.amount,
            sequence=transaction.sequence,
        )

        async with self.db.transaction():
            transaction_id = await self.db.execute(insert_statement)

            insert_statement = RELAYS.insert().values(
                transaction_id=transaction_id,
                status=transaction.relay_status,
                error=transaction.relay_error,
                message=transaction.relay_message,
                transaction_hash=None,
                grpc_status=transaction.relay_grpc_status,
                cache_status=transaction.relay_cache_status,
            )

            await self.db.execute(insert_statement)

    async def update(self, relay: UpdateRepoAdapter) -> None:
        """Updates relay object."""

        query = RELAYS.update()

        update_dict = relay.dict()

        if relay.transaction_hash is None:
            del update_dict["transaction_hash"]

        query = query.values(update_dict)

        update_statement = query.where(
            and_(
                TRANSACTIONS.c.emitter_address == relay.emitter_address.lower(),
                TRANSACTIONS.c.source_chain_id == relay.source_chain_id,
                TRANSACTIONS.c.sequence == relay.sequence,
                RELAYS.c.transaction_id == TRANSACTIONS.c.id,
            )
        )

        await self.db.execute(update_statement)

    async def update_relay_and_transaction(
        self, update_data: UpdateJoinedRepoAdapter
    ) -> None:
        """Update relay and transaction object."""

        where_clause = and_(
            TRANSACTIONS.c.emitter_address == update_data.emitter_address.lower(),
            TRANSACTIONS.c.source_chain_id == update_data.source_chain_id,
            TRANSACTIONS.c.sequence == update_data.sequence,
            RELAYS.c.transaction_id == TRANSACTIONS.c.id,
        )

        relays_update_statement = (
            RELAYS.update()
            .values(
                status=update_data.status,
                transaction_hash=update_data.transaction_hash,
                error=update_data.error,
                message=update_data.message,
            )
            .where(where_clause)
        )

        transactions_update_statement = (
            TRANSACTIONS.update()
            .values(
                from_address=update_data.from_address.lower(),
                to_address=update_data.to_address.lower(),
                dest_chain_id=update_data.dest_chain_id,
                amount=update_data.amount,
            )
            .where(where_clause)
        )

        async with self.db.transaction():
            await self.db.execute(relays_update_statement)
            await self.db.execute(transactions_update_statement)

    async def retrieve_failed(self) -> List[TransactionsJoinRelays]:
        """Retrieve all failed transactions that are not currently cached elsewhere."""

        query_conditions = [
            RELAYS.c.status == Status.FAILED,
            RELAYS.c.cache_status != CacheStatus.CURRENTLY_CACHED,
        ]

        j = TRANSACTIONS.join(RELAYS, TRANSACTIONS.c.id == RELAYS.c.transaction_id)

        columns_to_select = [
            TRANSACTIONS,
            RELAYS.c.id.label("relay_id"),
            RELAYS.c.status.label("relay_status"),
            RELAYS.c.error.label("relay_error"),
            RELAYS.c.message.label("relay_message"),
            RELAYS.c.transaction_hash.label("relay_transaction_hash"),
            RELAYS.c.cache_status.label("relay_cache_status"),
            RELAYS.c.grpc_status.label("relay_grpc_status"),
        ]

        query = select(columns_to_select).select_from(j).where(and_(*query_conditions))

        results = await self.db.fetch_all(query)

        return [TransactionsJoinRelays(**result) for result in results]

    async def get_latest_sequence(
        self,
        emitter_address: str,
        source_chain_id: int,
    ) -> Optional[TransactionsJoinRelays]:
        """Get the latest transaction for the given emitter_address and source_chain_id."""

        j = TRANSACTIONS.join(RELAYS, TRANSACTIONS.c.id == RELAYS.c.transaction_id)

        columns_to_select = [
            TRANSACTIONS,
            RELAYS.c.id.label("relay_id"),
            RELAYS.c.status.label("relay_status"),
            RELAYS.c.error.label("relay_error"),
            RELAYS.c.message.label("relay_message"),
            RELAYS.c.transaction_hash.label("relay_transaction_hash"),
            RELAYS.c.cache_status.label("relay_cache_status"),
            RELAYS.c.grpc_status.label("relay_grpc_status"),
        ]

        query = (
            select(columns_to_select)
            .select_from(j)
            .where(
                and_(
                    TRANSACTIONS.c.emitter_address == emitter_address.lower(),
                    TRANSACTIONS.c.source_chain_id == source_chain_id,
                )
            )
            .order_by(TRANSACTIONS.c.sequence.desc())
            .limit(1)
        )

        result = await self.db.fetch_one(query)

        return TransactionsJoinRelays(**result) if result else None

    async def retrieve_pending(self) -> List[TransactionsJoinRelays]:
        """Retrieves transactions that have been pending for longer than 1 minute."""

        query_conditions = [
            RELAYS.c.status == Status.PENDING,
            RELAYS.c.created_at < datetime.utcnow() - timedelta(minutes=1),
        ]

        j = TRANSACTIONS.join(RELAYS, TRANSACTIONS.c.id == RELAYS.c.transaction_id)

        columns_to_select = [
            TRANSACTIONS,
            RELAYS.c.id.label("relay_id"),
            RELAYS.c.status.label("relay_status"),
            RELAYS.c.error.label("relay_error"),
            RELAYS.c.message.label("relay_message"),
            RELAYS.c.transaction_hash.label("relay_transaction_hash"),
            RELAYS.c.cache_status.label("relay_cache_status"),
            RELAYS.c.grpc_status.label("relay_grpc_status"),
        ]

        query = select(columns_to_select).select_from(j).where(and_(*query_conditions))

        results = await self.db.fetch_all(query)

        return [TransactionsJoinRelays(**result) for result in results]
