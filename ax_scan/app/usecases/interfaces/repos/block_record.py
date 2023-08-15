from abc import ABC, abstractmethod
from typing import Optional

from app.usecases.schemas.block_record import BlockRecordInDb, BlockRecord


class IBlockRecordRepo(ABC):
    @abstractmethod
    async def upsert(self, block_record: BlockRecord) -> None:
        """Upserts a block_record."""

    @abstractmethod
    async def retrieve(self, chain_id: int) -> Optional[BlockRecordInDb]:
        """Retrieves block record by chain ID."""
