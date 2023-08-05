# pylint: disable=duplicate-code
import asyncio
import time
from logging import Logger
from typing import Mapping, Union

from databases import Database

from app.dependencies import CHAIN_DATA, LZ_LOOKUP, WH_LOOKUP
from app.settings import settings
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.interfaces.repos.messages import IMessagesRepo
from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.interfaces.tasks.gather_events import IGatherEventsTask
from app.usecases.schemas.tasks import TaskName
from app.usecases.schemas.evm_transaction import EvmTransaction, EvmTransactionStatus
from app.usecases.schemas.cross_chain_message import (
    WhCompositeIndex,
    LzCompositeIndex,
    WhMessage,
    LzMessage,
)
from app.usecases.schemas.cross_chain_transaction import (
    UpdateCrossChainTransaction,
    CrossChainTransaction,
)
from app.usecases.schemas.events import (
    SendToChain,
    ReceiveFromChain,
    BlockRange,
    EmitterAddress,
)
from app.usecases.schemas.bridge import Bridges


class GatherEventsTask(IGatherEventsTask):
    def __init__(
        self,
        db: Database,
        supported_evm_clients: Mapping[int, IEvmClient],
        transactions_repo: ITransactionsRepo,
        messages_repo: IMessagesRepo,
        tasks_repo: ITasksRepo,
        logger: Logger,
    ):
        self.db = db
        self.name = TaskName.GATHER_EVENTS
        self.transactions_repo = transactions_repo
        self.messages_repo = messages_repo
        self.tasks_repo = tasks_repo
        self.supported_evm_clients = supported_evm_clients
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
                        "[GatherPendingVaasTask]: Encountered lock; not performing task."
                    )
            except asyncio.CancelledError:  # pylint: disable = try-except-raise
                raise
            except Exception as e:  # pylint: disable = broad-except
                self.logger.exception(e)

            await asyncio.sleep(settings.gather_txs_frequency)

    async def task(self, task_id: int) -> None:
        """Gathers new transactions from blockchains."""

        self.logger.info("[GatherEventsTask]: Started.")
        task_start_time = time.time()

        for ax_chain_id, chain_data in CHAIN_DATA.items():
            evm_client = self.supported_evm_clients[ax_chain_id]

            block_range = await self.__get_block_range(ax_chain_id=ax_chain_id)

            # Process WormholeBridge events
            if chain_data.get("wh_chain_id"):
                events = await evm_client.fetch_events(
                    contract=settings.evm_wormhole_bridge,
                    from_block=block_range.from_block,
                    to_block=block_range.to_block,
                )

                for event in events:
                    await self.__store_event_data(ax_chain_id=ax_chain_id, event=event)

            # Process LayerZeroBridge events
            if chain_data.get("lz_chain_id"):
                events = await evm_client.fetch_events(
                    contract=settings.evm_layerzero_bridge,
                    from_block=block_range.from_block,
                    to_block=block_range.to_block,
                )

                for event in events:
                    await self.__store_event_data(ax_chain_id=ax_chain_id, event=event)

        await self.tasks_repo.delete_lock(task_id=task_id)

        self.logger.info(
            "[GatherEventsTask]: Finished; processed %s pending transactions in %s seconds.",
            len("something"),
            round(time.time() - task_start_time, 4),
        )

    async def __get_block_range(self, ax_chain_id: int) -> BlockRange:
        """Returns starting block and end block for a given chain's data query."""

        evm_client = self.supported_evm_clients[ax_chain_id]

        last_stored_block = await self.transactions_repo.retrieve_last_transaction(
            chain_id=ax_chain_id
        )

        latest_chain_blk_num = await evm_client.fetch_latest_block_number()

        # NOTE: does "- 1" work for all chains, including chains with high probability of re-orgs?
        max_upper_bound = latest_chain_blk_num - 1

        if last_stored_block is None:
            from_block = to_block = max_upper_bound
        else:
            from_block = last_stored_block.block_number + 1

            max_possible_to_block = (
                from_block + CHAIN_DATA[ax_chain_id]["max_block_range"]
            )

            to_block = min(max_possible_to_block, max_upper_bound)

        return BlockRange(from_block=from_block, to_block=to_block)

    async def __store_event_data(
        self, ax_chain_id: int, event: Union[SendToChain, ReceiveFromChain]
    ) -> None:
        """Stores chain event data in database."""

        if event.emitter_address == EmitterAddress.WORMHOLE_BRIDGE:
            ax_source_chain_id = WH_LOOKUP[event.source_chain_id]
            ax_dest_chain_id = WH_LOOKUP[event.dest_chain_id]
            existing_wh_message = await self.messages_repo.retrieve_wormhole_message(
                index=WhCompositeIndex(
                    emitter_address=event.emitter_address,
                    source_chain_id=event.source_chain_id,
                    sequence=event.message_id,
                )
            )

            async with self.db.transaction():
                # 1. Insert evm tx
                evm_tx_id = await self.transactions_repo.create_evm_tx(
                    evm_tx=EvmTransaction(
                        chain_id=ax_chain_id,
                        transaction_hash=event.transaction_hash,
                        block_hash=event.block_hash,
                        block_number=event.block_number,
                        status=EvmTransactionStatus.PENDING,
                    )
                )

                if existing_wh_message:
                    # 2. Update cross-chain tx
                    if isinstance(event, SendToChain):
                        update_values = UpdateCrossChainTransaction(
                            from_address=event.from_address,
                            source_chain_tx_id=evm_tx_id,
                        )
                    else:
                        update_values = UpdateCrossChainTransaction(
                            to_address=event.to_address, dest_chain_tx_id=evm_tx_id
                        )

                    await self.transactions_repo.update_cross_chain_tx(
                        cross_chain_tx_id=existing_wh_message.cross_chain_tx_id,
                        update_values=update_values,
                    ),
                else:
                    # 2. Insert cross-chain tx
                    if isinstance(event, SendToChain):
                        insert_values = CrossChainTransaction(
                            bridge=Bridges.WORMHOLE,
                            from_address=event.from_address,
                            source_chain_id=ax_source_chain_id,
                            dest_chain_id=ax_dest_chain_id,
                            amount=event.amount,
                            source_chain_tx_id=evm_tx_id,
                        )
                    else:
                        insert_values = CrossChainTransaction(
                            bridge=Bridges.WORMHOLE,
                            to_address=event.to_address,
                            source_chain_id=ax_source_chain_id,
                            dest_chain_id=ax_dest_chain_id,
                            amount=event.amount,
                            dest_chain_tx_id=evm_tx_id,
                        )

                    cross_chain_tx_id = (
                        await self.transactions_repo.create_cross_chain_tx(
                            cross_chain_tx=insert_values
                        )
                    )

                    # 3. Insert wormhole message
                    await self.messages_repo.create_wormhole_message(
                        cross_chain_tx_id=cross_chain_tx_id,
                        message=WhMessage(
                            emitter_address=event.emitter_address,
                            source_chain_id=event.source_chain_id,
                            sequence=event.message_id,
                        ),
                    )
        else:
            ax_source_chain_id = LZ_LOOKUP[event.source_chain_id]
            ax_dest_chain_id = LZ_LOOKUP[event.dest_chain_id]

            existing_lz_message = await self.messages_repo.retrieve_layer_zero_message(
                index=LzCompositeIndex(
                    emitter_address=event.emitter_address,
                    source_chain_id=event.source_chain_id,
                    dest_chain_id=event.dest_chain_id,
                    nonce=event.message_id,
                )
            )

            async with self.db.transaction():
                # 1. Insert evm tx
                evm_tx_id = await self.transactions_repo.create_evm_tx(
                    evm_tx=EvmTransaction(
                        chain_id=ax_chain_id,
                        transaction_hash=event.transaction_hash,
                        block_hash=event.block_hash,
                        block_number=event.block_number,
                        status=EvmTransactionStatus.PENDING,
                    )
                )

                if existing_lz_message:
                    # 2. Update cross-chain tx
                    if isinstance(event, SendToChain):
                        update_values = UpdateCrossChainTransaction(
                            from_address=event.from_address,
                            source_chain_tx_id=evm_tx_id,
                        )
                    else:
                        update_values = UpdateCrossChainTransaction(
                            to_address=event.to_address, dest_chain_tx_id=evm_tx_id
                        )

                    await self.transactions_repo.update_cross_chain_tx(
                        cross_chain_tx_id=existing_lz_message.cross_chain_tx_id,
                        update_values=update_values,
                    ),
                else:
                    # 2. Insert cross-chain tx
                    if isinstance(event, SendToChain):
                        insert_values = CrossChainTransaction(
                            bridge=Bridges.WORMHOLE,
                            from_address=event.from_address,
                            source_chain_id=ax_source_chain_id,
                            dest_chain_id=ax_dest_chain_id,
                            amount=event.amount,
                            source_chain_tx_id=evm_tx_id,
                        )
                    else:
                        insert_values = CrossChainTransaction(
                            bridge=Bridges.WORMHOLE,
                            to_address=event.to_address,
                            source_chain_id=ax_source_chain_id,
                            dest_chain_id=ax_dest_chain_id,
                            amount=event.amount,
                            dest_chain_tx_id=evm_tx_id,
                        )

                    cross_chain_tx_id = (
                        await self.transactions_repo.create_cross_chain_tx(
                            cross_chain_tx=insert_values
                        )
                    )

                    # 3. Insert layer zero message
                    await self.messages_repo.create_layer_zero_message(
                        cross_chain_tx_id=cross_chain_tx_id,
                        message=LzMessage(
                            emitter_address=event.emitter_address,
                            source_chain_id=event.source_chain_id,
                            dest_chain_id=event.dest_chain_id,
                            nonce=event.message_id,
                        ),
                    )
