import asyncio
from logging import Logger

from app.settings import settings
from app.usecases.interfaces.services.remote_price_manager import IRemotePriceManager
from app.usecases.interfaces.tasks.fee_update import IUpdateFeeTask


class UpdateFeesTask(IUpdateFeeTask):
    def __init__(self, remote_price_manager: IRemotePriceManager, logger: Logger):
        self.remote_price_manager = remote_price_manager
        self.logger = logger

    async def start_task(self) -> None:
        """Starts automated task to periodically update remote fees."""
        while True:
            try:
                await self.task()
            except asyncio.CancelledError:  # pylint: disable = try-except-raise
                raise
            except Exception as e:  # pylint: disable = broad-except
                self.logger.exception(e)

            await asyncio.sleep(settings.update_fees_frequency)

    async def task(self):
        """Update remote fees."""
        self.logger.info("[UpdateFeesTask]: Task started.")
        await self.remote_price_manager.update_remote_fees()
        self.logger.info("[UpdateFeesTask]: Task completed. Sleeping now...")
