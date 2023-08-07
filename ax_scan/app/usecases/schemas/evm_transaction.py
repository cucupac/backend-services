from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class EvmTransactionStatus(str, Enum):
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
    gas_price: Optional[int] = None
    gas_used: Optional[int] = None
    error: Optional[str] = None


class EvmTransactionInDb(EvmTransaction):
    """Database model."""

    id: int
    created_at: datetime
    updated_at: datetime


class UpdateEvmTransaction(BaseModel):
    status: EvmTransactionStatus
    gas_price: Optional[int] = None
    gas_used: Optional[int] = None
    error: Optional[str] = None
