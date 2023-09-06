from datetime import datetime

from pydantic import BaseModel


class PointsResponse(BaseModel):
    """Endpoint Response Model."""

    account: str
    points: int


class PointsInDb(BaseModel):
    """Database Model."""

    id: int
    account: str
    points: int
    created_at: datetime
    updated_at: datetime
