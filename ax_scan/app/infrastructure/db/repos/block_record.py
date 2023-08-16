from typing import Optional

from databases import Database
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.infrastructure.db.models.block_record import BLOCK_RECORD
from app.usecases.interfaces.repos.block_record import IBlockRecordRepo
from app.usecases.schemas.block_record import BlockRecord, BlockRecordInDb


class BlockRecordRepo(IBlockRecordRepo):
    def __init__(self, db: Database):
        self.db = db

    async def upsert(self, block_record: BlockRecord) -> None:
        """Upserts a block_record."""

        insert_stmt = insert(BLOCK_RECORD).values(
            chain_id=block_record.chain_id,
            last_scanned_block_number=block_record.last_scanned_block_number,
        )

        on_conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=["chain_id"],
            set_={"last_scanned_block_number": block_record.last_scanned_block_number},
        )

        await self.db.execute(on_conflict_stmt)

    async def retrieve(self, chain_id: int) -> Optional[BlockRecordInDb]:
        """Retrieves block record by chain ID."""

        query = select([BLOCK_RECORD]).where(BLOCK_RECORD.c.chain_id == chain_id)

        result = await self.db.fetch_one(query)

        return BlockRecordInDb(**result) if result else None
