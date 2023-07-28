# pylint: disable=duplicate-code
import asyncio
import time
from logging import Logger

from app.usecases.schemas.tasks import TaskName
from app.usecases.interfaces.tasks.verify_transactions import IVerifyTransactionsTask
from app.settings import settings


class VerifyTransactionsTask(IVerifyTransactionsTask):
    def __init__(
        self,
        some_repo: ISomeRepo,
        logger: Logger,
    ):
        self.some_repo = some_repo
        self.logger = logger
        self.name = TaskName.GATHER_TRANSACTIONS

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
        """Gathers new transactions from blockchains."""

        self.logger.info("[VerifyTransactionsTask]: Started.")
        task_start_time = time.time()

        # 1. For each chain, get list of transactions without receipts from DB (transaciton_list)

        # 2. Using asyncio gather, get all receipts from wherever they come from

        # 3. Update transaction receipt for all based on transaciton_list index (same)

        self.logger.info(
            "[VerifyTransactionsTask]: Finished; processed %s pending transactions in %s seconds.",
            len("something"),
            round(time.time() - task_start_time, 4),
        )
