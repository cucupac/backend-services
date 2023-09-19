from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, validator


class MintData(BaseModel):
    account: str
    amount: int


class MintInDb(MintData):
    """Database Model."""

    id: int
    chain_tx_id: int
    created_at: datetime
    updated_at: datetime

    @validator("amount", pre=True)
    def convert_amount_to_int(cls, value):  # pylint: disable = no-self-argument
        if isinstance(value, Decimal):
            return int(value)
        return value
