from typing import List, Optional

from databases import Database
from sqlalchemy import and_, select
from sqlalchemy.dialects.postgresql import insert

from app.infrastructure.db.models.relays import RELAYS
from app.infrastructure.db.models.transactions import TRANSACTIONS
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.schemas.relays import CacheStatus, GrpcStatus, RelayErrors, Status
from app.usecases.schemas.transactions import (
    CreateRepoAdapter,
    RetriveManyRepoAdapter,
    TransactionsJoinRelays,
)


class TransactionsRepo(ITransactionsRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(self, transaction: CreateRepoAdapter) -> TransactionsJoinRelays:
        """Inserts and returns new transaction object."""
        most_recent_record = await self.get_latest_sequence(
            emitter_address=transaction.emitter_address,
            source_chain_id=transaction.source_chain_id,
        )

        if most_recent_record is not None:
            if most_recent_record.sequence != transaction.sequence - 1:
                sequence_to_insert = most_recent_record.sequence + 1
                while sequence_to_insert < transaction.sequence:
                    insert_statement = (
                        insert(TRANSACTIONS)
                        .values(
                            emitter_address=transaction.emitter_address.lower(),
                            from_address=None,
                            to_address=None,
                            source_chain_id=transaction.source_chain_id,
                            dest_chain_id=None,
                            amount=None,
                            sequence=sequence_to_insert,
                        )
                        .on_conflict_do_nothing()
                    )

                    async with self.db.transaction():
                        transaction_id = await self.db.execute(insert_statement)

                        insert_statement = (
                            insert(RELAYS)
                            .values(
                                transaction_id=transaction_id,
                                status=Status.FAILED,
                                error=RelayErrors.MISSED_VAA,
                                message=None,
                                transaction_hash=None,
                                grpc_status=GrpcStatus.FAILED,
                                cache_status=CacheStatus.NEVER_CACHED,
                            )
                            .on_conflict_do_nothing()
                        )

                        if transaction_id:
                            await self.db.execute(insert_statement)
                    sequence_to_insert += 1

        insert_statement = insert(TRANSACTIONS).values(
            emitter_address=transaction.emitter_address.lower(),
            source_chain_id=transaction.source_chain_id,
            sequence=transaction.sequence,
            from_address=transaction.from_address.lower(),
            to_address=transaction.to_address.lower(),
            dest_chain_id=transaction.dest_chain_id,
            amount=transaction.amount,
        )

        upsert_statement = insert_statement.on_conflict_do_update(
            index_elements=[
                TRANSACTIONS.c.emitter_address,
                TRANSACTIONS.c.source_chain_id,
                TRANSACTIONS.c.sequence,
            ],
            set_={
                "from_address": transaction.from_address.lower(),
                "to_address": transaction.to_address.lower(),
                "dest_chain_id": transaction.dest_chain_id,
                "amount": transaction.amount,
            },
        )

        async with self.db.transaction():
            transaction_id = await self.db.execute(upsert_statement)

            insert_statement = insert(RELAYS).values(
                transaction_id=transaction_id,
                status=transaction.relay_status,
                error=transaction.relay_error,
                message=transaction.relay_message,
                transaction_hash=None,
                cache_status=transaction.relay_cache_status,
                grpc_status=GrpcStatus.SUCCESS,
            )

            upsert_statement = insert_statement.on_conflict_do_update(
                index_elements=[RELAYS.c.transaction_id],
                set_={
                    "status": transaction.relay_status,
                    "error": transaction.relay_error,
                    "message": transaction.relay_message,
                    "cache_status": transaction.relay_cache_status,
                    "grpc_status": GrpcStatus.SUCCESS,
                },
            )

            await self.db.execute(upsert_statement)

        return await self.retrieve(transaction_id=transaction_id)

    async def retrieve(
        self,
        transaction_id: int,
    ) -> Optional[TransactionsJoinRelays]:
        """Retrieve transaction object with relay information."""
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
            .where(TRANSACTIONS.c.id == transaction_id)
        )

        result = await self.db.fetch_one(query)

        return TransactionsJoinRelays(**result) if result else None

    async def retrieve_many(
        self,
        query_params: RetriveManyRepoAdapter,
    ) -> List[TransactionsJoinRelays]:
        """Retrieve transaction object with relay information."""

        query_conditions = []

        if query_params.relay_status:
            query_conditions.append(RELAYS.c.status == query_params.relay_status)

        if query_params.from_address:
            query_conditions.append(
                TRANSACTIONS.c.from_address == query_params.from_address.lower()
            )

        if query_params.to_address:
            query_conditions.append(
                TRANSACTIONS.c.to_address == query_params.to_address.lower()
            )

        if not query_conditions:
            return

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
