from databases import Database
from sqlalchemy import and_

# TODO: think about placing in shared directory, if not definiting new schemas (might not want for stuff like this -- details -- only library)
from app.infrastructure.db.models.relays import RELAYS
from app.infrastructure.db.models.transactions import TRANSACTIONS
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.schemas.relays import UpdateRepoAdapter


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
