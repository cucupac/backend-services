from typing import List

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
from app.usecases.schemas.transactions import TransactionsJoinRelays


class RelaysRepo(IRelaysRepo):
    def __init__(self, db: Database):
        self.db = db

    async def update(self, relay: UpdateRepoAdapter) -> None:
        """Update relay object."""

        update_statement = (
            RELAYS.update()
            .values(
                status=relay.status,
                transaction_hash=relay.transaction_hash,
                error=relay.error,
            )
            .where(
                and_(
                    TRANSACTIONS.c.emitter_address == relay.emitter_address,
                    TRANSACTIONS.c.source_chain_id == relay.source_chain_id,
                    TRANSACTIONS.c.sequence == relay.sequence,
                    RELAYS.c.transaction_id == TRANSACTIONS.c.id,
                )
            )
        )

        await self.db.execute(update_statement)

    async def update_relay_and_transaction(
        self, update_data: UpdateJoinedRepoAdapter
    ) -> None:
        """Update relay and transaction object."""

        where_clause = and_(
            TRANSACTIONS.c.emitter_address == update_data.emitter_address,
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
            )
            .where(where_clause)
        )

        transactions_update_statement = (
            TRANSACTIONS.update()
            .values(
                from_address=update_data.from_address,
                to_address=update_data.to_address,
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
        ]

        query = select(columns_to_select).select_from(j).where(and_(*query_conditions))

        results = await self.db.fetch_all(query)

        return [TransactionsJoinRelays(**result) for result in results]
