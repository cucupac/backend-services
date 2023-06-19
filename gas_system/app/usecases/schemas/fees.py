from datetime import datetime
from enum import Enum
from typing import List, Mapping, Optional

from pydantic import BaseModel

from app.usecases.schemas.blockchain import Chains


class Status(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"


class FeeUpdateError(str, Enum):
    DESTINATION_PRICE_TOO_HIGH = "One or more destination prices were too high."
    TX_FEE_TOO_HIGH = (
        "Fee update transaction fee was too high; waiting for a cheaper price."
    )


class MinimumFees(BaseModel):
    remote_chain_ids: List[Chains]
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
