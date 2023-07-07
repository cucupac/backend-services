from databases import Database

from app.infrastructure.db.models.fee_updates import FEE_UPDATES
from app.usecases.interfaces.repos.fee_updates import IFeeUpdatesRepo
from app.usecases.schemas.fees import FeeUpdate, FeeUpdateInDb


class FeeUpdatesRepo(IFeeUpdatesRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(self, fee_update: FeeUpdate) -> FeeUpdateInDb:
        """Inserts and returns new fee update object."""

        insert_statement = FEE_UPDATES.insert().values(
            chain_id=fee_update.chain_id,
            updates=fee_update.updates,
            transaction_hash=fee_update.transaction_hash,
            status=fee_update.status,
            error=fee_update.error,
        )

        fee_update_id = await self.db.execute(insert_statement)

        return await self.retrieve(fee_update_id=fee_update_id)

    async def retrieve(self, fee_update_id: int) -> FeeUpdateInDb:
        """Retrieves a fee update object."""

        query = FEE_UPDATES.select().where(FEE_UPDATES.c.id == fee_update_id)

        result = await self.db.fetch_one(query)
        return FeeUpdateInDb(**result) if result else None

    async def retrieve_last_update_by_chain_id(self, chain_id: int) -> FeeUpdateInDb:
        """Retrieves the last recorded fee update by chain ID."""

        query = (
            FEE_UPDATES.select()
            .where(FEE_UPDATES.c.chain_id == chain_id)
            .order_by(FEE_UPDATES.c.created_at.desc())
            .limit(1)
        )

        result = await self.db.fetch_one(query)
        return FeeUpdateInDb(**result) if result else None
