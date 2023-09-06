from datetime import datetime, timedelta
from typing import List, Optional

from databases import Database
from sqlalchemy import select

from app.infrastructure.db.models.mints import MINTS
from app.usecases.interfaces.repos.mints import IMintsRepo
from app.usecases.schemas.mints import MintData, MintInDb


class MintsRepo(IMintsRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(self, tx_id: int, mint_data: MintData) -> Optional[int]:
        """Inserts a mint; returns mints id."""

        mint_insert_stmt = MINTS.insert().values(
            chain_tx_id=tx_id, account=mint_data.account, amount=mint_data.amount
        )

        return await self.db.execute(mint_insert_stmt)

    async def retrieve_all_recent_mints(
        self,
    ) -> List[MintInDb]:
        """Retrieves total recent mints; returns a list of database mints."""

        query = select([MINTS]).where(
            MINTS.c.created_at > datetime.utcnow() - timedelta(weeks=1)
        )

        results = await self.db.fetch_all(query)

        return [MintInDb(**result) for result in results]
