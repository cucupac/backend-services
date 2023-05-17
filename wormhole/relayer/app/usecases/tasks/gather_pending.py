# pylint: disable=duplicate-code
import asyncio
from logging import Logger

from app.settings import settings
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.interfaces.tasks.gather_pending import IGatherPendingVaasTask
from app.usecases.schemas.relays import RelayErrors, Status, UpdateRepoAdapter


class GatherPendingVaasTask(IGatherPendingVaasTask):
    def __init__(
        self,
        relays_repo: IRelaysRepo,
        logger: Logger,
    ):
        self.relays_repo = relays_repo
        self.logger = logger

    async def start_task(self) -> None:
        """Starts automated task to periodically check for messages that have been pending for too long."""
        while True:
            try:
                await self.task()
            except asyncio.CancelledError:  # pylint: disable = try-except-raise
                raise
            except Exception as e:  # pylint: disable = broad-except
                self.logger.exception(e)

            await asyncio.sleep(settings.gather_pending_frequency)

    async def task(self):
        """Retries untracked transactions."""
        self.logger.info("[GatherPendingVaasTask]: Task started.")

        transactions = await self.relays_repo.retrieve_pending()

        for transaction in transactions:
            await self.relays_repo.update(
                relay=UpdateRepoAdapter(
                    emitter_address=transaction.emitter_address,
                    source_chain_id=transaction.source_chain_id,
                    sequence=transaction.sequence,
                    transaction_hash=None,
                    error=RelayErrors.STALE_PENDING,
                    status=Status.FAILED,
                )
            )

        self.logger.info("[GatherPendingVaasTask]: Finished; sleeping now...")
