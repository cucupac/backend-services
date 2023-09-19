from abc import ABC, abstractmethod
from typing import Optional

from app.usecases.schemas.block_record import BlockRecord, BlockRecordInDb


class IBlockRecordRepo(ABC):
    @abstractmethod
    async def upsert(self, block_record: BlockRecord) -> None:
        """Upserts a block_record."""

    @abstractmethod
    async def retrieve(self, task_id: int, chain_id: int) -> Optional[BlockRecordInDb]:
        """Retrieves block record by chain ID."""
