import asyncio

from app.dependencies import logger
from app.settings import settings


class UpdateFeesTask:
    def __init__(self, db: Database, something_repo: ISomethingRepo):
        self.db = db
        self.something_repo = something_repo

    async def start_task(self):
        while True:
            try:
                await self.task()
            except asyncio.CancelledError:  # pylint: disable = try-except-raise
                raise
            except Exception as e:  # pylint: disable = broad-except
                logger.exception(e)

            await asyncio.sleep(settings.update_fees_frequency)

    async def task(self):
        """Refresh tokens for all linked brokerages that require it."""

        # 1. call update_remote_prices on remote_price_manager service

        # 2. store stuff in db
