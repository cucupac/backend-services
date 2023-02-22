from databases import Database

from app.infrastructure.db.models.fee_updates import FEE_UPDATES
from app.usecases.interfaces.repos.fee_updates import IFeeUpdateRepo
from app.usecases.schemas.fees import FeeUpdate


class FeeUpdateRepo(IFeeUpdateRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(self, fee_update: FeeUpdate) -> None:
        """Inserts and returns new fee update object."""

        insert_statement = FEE_UPDATES.insert().values(
            chain_id=fee_update.chain_id,
            udpates=fee_update.udpates,
            transaction_hash=fee_update.transaction_hash,
            error=fee_update.error,
        )

        await self.db.execute(insert_statement)
