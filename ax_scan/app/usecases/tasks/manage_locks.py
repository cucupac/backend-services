# pylint: disable=duplicate-code
import asyncio
from datetime import datetime, timedelta
from logging import Logger

from app.settings import settings
from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.interfaces.tasks.manage_locks import IManageLocksTask


class ManageLocksTask(IManageLocksTask):
    def __init__(
        self,
        tasks_repo: ITasksRepo,
        logger: Logger,
    ):
        self.tasks_repo = tasks_repo
        self.logger = logger

    async def start_task(self) -> None:
        while True:
            try:
                await self.task()
            except asyncio.CancelledError:  # pylint: disable = try-except-raise
                raise
            except Exception as e:  # pylint: disable = broad-except
                self.logger.exception(e)

            await asyncio.sleep(settings.manage_locks_frequency)

    async def task(self) -> None:
        """Removes stale locks if they exist."""

        self.logger.info("[ManageLocksTask]: Started.")

        task_locks = await self.tasks_repo.retrieve_all_locks()

        stale_locks_count = 0
        for lock in task_locks:
            if lock.created_at < datetime.utcnow() - timedelta(minutes=5):
                await self.tasks_repo.delete_lock(task_id=lock.task_id)
                stale_locks_count += 1

        self.logger.info(
            "[ManageLocksTask]: Finished; removed %s stale locks.", stale_locks_count
        )
