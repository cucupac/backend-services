import asyncio
from datetime import datetime, timedelta
from logging import Logger

from app.dependencies import CHAIN_DATA, UPDATE_FEES_FREQUENCIES
from app.settings import settings
from app.usecases.interfaces.repos.fee_updates import IFeeUpdatesRepo
from app.usecases.interfaces.services.remote_price_manager import IRemotePriceManager
from app.usecases.interfaces.tasks.fee_update import IUpdateFeeTask
from app.usecases.schemas.fees import Status


class UpdateFeesTask(IUpdateFeeTask):
    def __init__(
        self,
        remote_price_manager: IRemotePriceManager,
        fee_updates_repo: IFeeUpdatesRepo,
        logger: Logger,
    ):
        self.remote_price_manager = remote_price_manager
        self.fee_updates_repo = fee_updates_repo
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

            await asyncio.sleep(settings.update_fees_task_frequency)

    async def task(self):
        """Update remote fees."""
        self.logger.info("[UpdateFeesTask]: Started.")

        # Determine which chains need to be updated
        chains_to_update = []
        for ax_chain_id in CHAIN_DATA:
            last_fee_update = (
                await self.fee_updates_repo.retrieve_last_update_by_chain_id(
                    chain_id=ax_chain_id
                )
            )

            if not last_fee_update:
                chains_to_update.append(ax_chain_id)
            else:
                if last_fee_update.status == Status.FAILED:
                    chains_to_update.append(ax_chain_id)
                else:
                    if last_fee_update.created_at <= datetime.utcnow() - timedelta(
                        seconds=UPDATE_FEES_FREQUENCIES[ax_chain_id]
                    ):
                        chains_to_update.append(ax_chain_id)

        if chains_to_update:
            await self.remote_price_manager.update_remote_fees(
                chains_to_update=chains_to_update
            )

        self.logger.info(
            "[UpdateFeesTask]: Task complete. Attempted to update chains: %s",
            chains_to_update,
        )
