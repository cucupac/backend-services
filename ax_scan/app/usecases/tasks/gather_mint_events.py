# pylint: disable=duplicate-code,too-many-instance-attributes,too-many-arguments,too-many-branches
import asyncio
import time
from logging import Logger
from typing import List

from databases import Database

from app.dependencies import CHAIN_DATA
from app.settings import settings
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.interfaces.repos.block_record import IBlockRecordRepo
from app.usecases.interfaces.repos.mints import IMintsRepo
from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.interfaces.tasks.gather_mint_events import IGatherMintEventsTask
from app.usecases.schemas.block_record import BlockRecord
from app.usecases.schemas.blockchain import AxChains
from app.usecases.schemas.events import BlockRange, EmitterAddress, Mint
from app.usecases.schemas.evm_transaction import EvmTransaction, EvmTransactionStatus
from app.usecases.schemas.mints import MintData
from app.usecases.schemas.tasks import TaskName


class GatherMintEventsTask(IGatherMintEventsTask):
    def __init__(
        self,
        db: Database,
        evm_client: IEvmClient,
        transactions_repo: ITransactionsRepo,
        mints_repo: IMintsRepo,
        block_record_repo: IBlockRecordRepo,
        tasks_repo: ITasksRepo,
        logger: Logger,
    ):
        self.db = db
        self.name = TaskName.GATHER_MINT_EVENTS
        self.transactions_repo = transactions_repo
        self.mints_repo = mints_repo
        self.block_recoreds_repo = block_record_repo
        self.tasks_repo = tasks_repo
        self.evm_client = evm_client
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
                        "[GatherMintEventsTask]: Encountered lock; not performing task."
                    )
            except asyncio.CancelledError:  # pylint: disable = try-except-raise
                raise
            except Exception as e:  # pylint: disable = broad-except
                self.logger.exception(e)

            await asyncio.sleep(settings.gather_txs_frequency)

    async def task(self, task_id: int) -> None:
        """Gathers new mint transactions from the Treasury contract."""

        self.logger.info("[GatherMintEventsTask]: Started.")
        task_start_time = time.time()

        event_count = 0

        block_ranges = await self.get_block_range(ax_chain_id=AxChains.ETHEREUM)

        for block_range in block_ranges:
            events = await self.evm_client.fetch_mint_events(
                contract=EmitterAddress.TREASURY,
                from_block=block_range.from_block,
                to_block=block_range.to_block,
            )

            for event in events:
                await self.__store_event_data(event=event)
                event_count += 1

            # Update block record
            await self.block_recoreds_repo.upsert(
                block_record=BlockRecord(
                    chain_id=AxChains.ETHEREUM,
                    last_scanned_block_number=block_range.to_block,
                )
            )

        await self.tasks_repo.delete_lock(task_id=task_id)

        self.logger.info(
            "[GatherMintEventsTask]: Finished; processed %s events in %s seconds.",
            event_count,
            round(time.time() - task_start_time, 4),
        )

    async def get_block_range(self, ax_chain_id: int) -> List[BlockRange]:
        """Returns a list of starting and ending blocks for a given chain's data query."""

        # Obtain upper and lower bounds
        last_scanned_block = await self.block_recoreds_repo.retrieve(
            chain_id=ax_chain_id
        )

        latest_chain_blk_num = await self.evm_client.fetch_latest_block_number()

        upper_bound = latest_chain_blk_num - 1

        # Construct block range
        block_ranges = []
        if not last_scanned_block:
            block_ranges.append(
                BlockRange(from_block=upper_bound, to_block=upper_bound)
            )
        else:
            from_block = last_scanned_block.last_scanned_block_number + 1
            max_to_block = from_block + CHAIN_DATA[ax_chain_id]["query_size"]
            while max_to_block < upper_bound:
                block_ranges.append(
                    BlockRange(from_block=from_block, to_block=max_to_block)
                )
                from_block = max_to_block + 1
                max_to_block = from_block + CHAIN_DATA[ax_chain_id]["query_size"]
            from_block = upper_bound if from_block > upper_bound else from_block
            block_ranges.append(BlockRange(from_block=from_block, to_block=upper_bound))

        return block_ranges

    async def __store_event_data(self, event: Mint) -> None:
        """Stores chain event data in database."""

        async with self.db.transaction():
            evm_tx_id = await self.transactions_repo.create_evm_tx(
                evm_tx=EvmTransaction(
                    chain_id=AxChains.ETHEREUM,
                    transaction_hash=event.transaction_hash,
                    block_hash=event.block_hash,
                    block_number=event.block_number,
                    status=EvmTransactionStatus.PENDING,
                )
            )
            if evm_tx_id:
                await self.mints_repo.create(
                    tx_id=evm_tx_id,
                    mint_data=MintData(account=event.account, amount=event.amount),
                )
