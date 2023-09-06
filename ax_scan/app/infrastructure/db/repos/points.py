from typing import Optional

from databases import Database
from sqlalchemy import select

from app.infrastructure.db.models.points import POINTS
from app.usecases.interfaces.repos.points import IPointsRepo
from app.usecases.schemas.points import PointsInDb


class PointsRepo(IPointsRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(self, account: str, points: int) -> None:
        """Upserts account's points."""

        insert_stmt = POINTS.insert().values(
            account=account,
            points=points,
        )

        await self.db.execute(insert_stmt)

    async def update(self, account: str, points: int) -> None:
        """Updates account's points."""

        update_stmt = (
            POINTS.update()
            .values(
                points=points,
            )
            .where(POINTS.c.account == account)
        )

        await self.db.execute(update_stmt)

    async def retrieve(self, account: str) -> Optional[PointsInDb]:
        """Retrieves account's points; returns database object."""

        query = select([POINTS]).where(
            POINTS.c.account == account,
        )

        result = await self.db.fetch_one(query)

        return PointsInDb(**result) if result else None
