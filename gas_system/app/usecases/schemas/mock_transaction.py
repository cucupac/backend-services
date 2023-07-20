from datetime import datetime

from pydantic import BaseModel


class MockTransactionInDb(BaseModel):
    """Database Model."""

    id: int
    chain_id: int
    payload: str
    created_at: datetime
    updated_at: datetime
