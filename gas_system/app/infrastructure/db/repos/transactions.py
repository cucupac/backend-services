from databases import Database
from sqlalchemy import select, and_

from app.infrastructure.db.models.relays import RELAYS
from app.infrastructure.db.models.transactions import TRANSACTIONS
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.schemas.transactions import TransactionsJoinRelays, Status


class TransactionsRepo(ITransactionsRepo):
    def __init__(self, db: Database):
        self.db = db

    async def retrieve_testing_by_chain_id(
        self, chain_id: int
    ) -> TransactionsJoinRelays:
        """Retrieves relays with status of `testing`."""

        query_conditions = [
            RELAYS.c.status == Status.TESTING,
            TRANSACTIONS.c.dest_chain_id == chain_id,
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

        result = await self.db.fetch_one(query)

        return TransactionsJoinRelays(**result) if result else None
