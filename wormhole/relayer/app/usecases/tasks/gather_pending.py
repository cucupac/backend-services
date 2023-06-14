# pylint: disable=duplicate-code
import asyncio
import time
from logging import Logger

from app.settings import settings
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.interfaces.tasks.gather_pending import IGatherPendingVaasTask
from app.usecases.schemas.relays import RelayErrors, Status, UpdateRepoAdapter
from app.usecases.schemas.tasks import TaskName


class GatherPendingVaasTask(IGatherPendingVaasTask):
    def __init__(
        self,
        relays_repo: IRelaysRepo,
        tasks_repo: ITasksRepo,
        logger: Logger,
    ):
        self.relays_repo = relays_repo
        self.tasks_repo = tasks_repo
        self.logger = logger
        self.name = TaskName.GATHER_PENDING

    async def start_task(self) -> None:
        while True:
            try:
                # Check distributed lock for task availability.
                task = await self.tasks_repo.retrieve(task_name=self.name)
                available_task = await self.tasks_repo.create_lock(task_id=task.id)
                if available_task:
                    await self.task(task_id=task.id)
                else:
                    self.logger.info(
                        "[GatherPendingVaasTask]: Encountered lock; not performing task."
                    )
            except asyncio.CancelledError:  # pylint: disable = try-except-raise
                raise
            except Exception as e:  # pylint: disable = broad-except
                self.logger.exception(e)

            await asyncio.sleep(settings.gather_pending_frequency)

    async def task(self, task_id: int) -> None:
        """Marks stale transactions as failed."""

        self.logger.info("[GatherPendingVaasTask]: Started.")
        task_start_time = time.time()

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
            self.logger.info(
                "[GatherPendingVaasTask]: Rescued stale pending; chain id: %s, sequence: %s",
                transaction.source_chain_id,
                transaction.sequence,
            )

        await self.tasks_repo.delete_lock(task_id=task_id)

        self.logger.info(
            "[GatherPendingVaasTask]: Finished; processed %s pending transactions in %s seconds.",
            len(transactions),
            round(time.time() - task_start_time, 4),
        )
