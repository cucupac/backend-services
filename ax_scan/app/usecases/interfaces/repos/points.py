from abc import ABC, abstractmethod
from typing import Optional

from app.usecases.schemas.points import PointsInDb


class IPointsRepo(ABC):
    @abstractmethod
    async def create(self, account: str, points: int) -> None:
        """Creates account's points."""

    @abstractmethod
    async def update(self, account: str, points: int) -> None:
        """Updates account's points."""

    @abstractmethod
    async def retrieve(self, account: str) -> Optional[PointsInDb]:
        """Retrieves account's points; returns database object."""
