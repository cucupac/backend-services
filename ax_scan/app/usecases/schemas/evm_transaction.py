from typing import Optional
from enum import Enum
from datetime import datetime

from pydantic import BaseModel


class EvmTransactionStatus(Enum):
    SUCCESS = "success"
    PENDING = "pending"
    FAILED = "failed"


class EvmTransaction(BaseModel):
    """A blockchain transaction."""

    chain_id: int
    transaction_hash: str
    block_hash: str
    block_number: int
    status: EvmTransactionStatus
    gas_price: Optional[int]
    gas_used: Optional[int]
    timestamp: Optional[int]


class EvmTransactionInDb(EvmTransaction):
    """Database model."""

    id: int
    created_at: datetime
    updated_at: datetime
