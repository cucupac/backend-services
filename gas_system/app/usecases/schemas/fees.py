from datetime import datetime
from enum import Enum
from typing import List, Mapping, Optional

from pydantic import BaseModel

from app.usecases.schemas.blockchain import AxChains


class Status(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"


class MinimumFees(BaseModel):
    remote_chain_ids: List[AxChains]
    remote_fees: List[int]


class FeeUpdate(BaseModel):
    chain_id: int
    updates: Mapping[int, int]
    transaction_hash: Optional[str]
    status: Status
    error: Optional[str]


class FeeUpdateInDb(FeeUpdate):
    id: int
    created_at: datetime
    updated_at: datetime
