from datetime import datetime

from pydantic import BaseModel


class BlockRecord(BaseModel):
    chain_id: int
    last_scanned_block_number: int


class BlockRecordInDb(BlockRecord):
    """Database Model."""

    id: int
    created_at: datetime
    updated_at: datetime
