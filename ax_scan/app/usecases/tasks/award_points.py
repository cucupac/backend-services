# pylint: disable=duplicate-code
import asyncio
from datetime import datetime, timedelta
from logging import Logger

from app.settings import settings
from app.usecases.interfaces.repos.mints import IMintsRepo
from app.usecases.interfaces.repos.points import IPointsRepo
from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.interfaces.tasks.award_points import IAwardPointsTask
from app.usecases.schemas.tasks import TaskName


class AwardPointsTask(IAwardPointsTask):
    def __init__(
        self,
        points_repo: IPointsRepo,
        mints_repo: IMintsRepo,
        tasks_repo: ITasksRepo,
        logger: Logger,
    ):
        self.name = TaskName.AWARD_POINTS
        self.total_points = 1000
        self.points_repo = points_repo
        self.mints_repo = mints_repo
        self.tasks_repo = tasks_repo
        self.logger = logger

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
                        "[AwardPointsTask]: Encountered lock; not performing task."
                    )
            except asyncio.CancelledError:  # pylint: disable = try-except-raise
                raise
            except Exception as e:  # pylint: disable = broad-except
                self.logger.exception(e)

            await asyncio.sleep(settings.award_points_frequency)

    async def task(self, task_id: int) -> None:
        """Removes stale locks if they exist."""

        self.logger.info("[AwardPointsTask]: Started.")

        # 1. get total amount minted in the last week
        recent_mints = await self.mints_repo.retrieve_all_recent_mints()

        mints = {}
        total_minted = 0
        for mint in recent_mints:
            mints[mint.account] = mints.get(mint.account, 0) + mint.amount
            total_minted += mint.amount

        for account, total_account_mint in mints.items():
            mint_percentage = total_account_mint / total_minted

            reward = mint_percentage * self.total_points

            # 2. Save points
            current_points = await self.points_repo.retrieve(account=account)
            if current_points:
                if current_points.updated_at <= datetime.utcnow() - timedelta(weeks=1):
                    await self.points_repo.update(
                        account=account, points=current_points.points + reward
                    )
            else:
                await self.points_repo.create(account=account, points=reward)

        await self.tasks_repo.delete_lock(task_id=task_id)

        self.logger.info("[AwardPointsTask]: Finished.")
