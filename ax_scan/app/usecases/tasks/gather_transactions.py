# pylint: disable=duplicate-code
import time
from typing import Mapping
from logging import Logger

import asyncio

from app.dependencies import BRIDGE_DATA
from app.usecases.schemas.tasks import TaskName
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.interfaces.tasks.gather_transactions import IGatherTransactionsTask
from app.settings import settings


class GatherTransactionsTask(IGatherTransactionsTask):
    def __init__(
        self,
        supported_evm_clients: Mapping[int, IEvmClient],
        some_repo: ISomeRepo,
        logger: Logger,
    ):
        self.some_repo = some_repo
        self.logger = logger
        self.supported_evm_clients = supported_evm_clients
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

        self.logger.info("[GatherTransactionsTask]: Started.")
        task_start_time = time.time()

        for chain_id, bridge_data in BRIDGE_DATA.items():
            pass

        # 1. For each chain, get last block number
        # For this, we'll need to look at the chain_transactions table and the cross_chain_transactions table (JOIN)
        # This task only grabs source and dest transactions, not other arbitrary ones. Ones like fee updates are placed in themselves

        # 2. ask for the block range until like 2 blocks ago, so not recent

        # 3. Parse data into 2 lists: one for SendToChain, the other for ReceiveFromChain

        self.logger.info(
            "[GatherTransactionsTask]: Finished; processed %s pending transactions in %s seconds.",
            len("something"),
            round(time.time() - task_start_time, 4),
        )
