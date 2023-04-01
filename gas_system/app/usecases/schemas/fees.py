from datetime import datetime
from typing import List, Mapping, Optional

from pydantic import BaseModel

from app.usecases.schemas.blockchain import Chains


class MinimumFees(BaseModel):
    remote_chain_ids: List[Chains]
    remote_fees: List[int]


class FeeUpdate(BaseModel):
    chain_id: int
    updates: Mapping[int, int]
    transaction_hash: Optional[str]
    error: Optional[str]


class FeeUpdateInDb(FeeUpdate):
    id: int
    created_at: datetime
    updated_at: datetime
