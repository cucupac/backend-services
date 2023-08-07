# pylint: disable=duplicate-code
from typing import Mapping, List
import time
from logging import Logger

import asyncio

from app.settings import settings
from app.dependencies import CHAIN_DATA
from app.usecases.interfaces.tasks.verify_transactions import IVerifyTransactionsTask
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.schemas.tasks import TaskName
from app.usecases.schemas.blockchain import (
    TransactionReceiptResponse,
    BlockchainClientError,
    BlockchainErrors,
)
from app.usecases.schemas.evm_transaction import (
    EvmTransactionStatus,
    UpdateEvmTransaction,
)


class VerifyTransactionsTask(IVerifyTransactionsTask):
    def __init__(
        self,
        supported_evm_clients: Mapping[int, IEvmClient],
        transactions_repo: ITransactionsRepo,
        tasks_repo: ITasksRepo,
        logger: Logger,
    ):
        self.supported_evm_clients = supported_evm_clients
        self.transactions_repo = transactions_repo
        self.tasks_repo = tasks_repo
        self.logger = logger
        self.name = TaskName.GATHER_EVENTS

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
                        "[VerifyTransactionsTask]: Encountered lock; not performing task."
                    )
            except asyncio.CancelledError:  # pylint: disable = try-except-raise
                raise
            except Exception as e:  # pylint: disable = broad-except
                self.logger.exception(e)

            await asyncio.sleep(settings.verify_txs_frequency)

    async def task(self, task_id: int) -> None:
        """Gathers pending transactions for verification."""

        self.logger.info("[VerifyTransactionsTask]: Started.")
        task_start_time = time.time()
        tx_count = 0

        # 1. For each chain, retrieve the pending transactions
        for ax_chain_id in CHAIN_DATA:
            pending_txs = await self.transactions_repo.retrieve_pending(
                chain_id=ax_chain_id
            )

            get_receipt_tasks = [
                asyncio.create_task(
                    self.__get_transaction_receipt(
                        ax_chain_id=ax_chain_id, tx_hash=tx.transaction_hash
                    )
                )
                for tx in pending_txs
            ]

            # 2. Fetch transaction receipts
            receipt_list: List[TransactionReceiptResponse] = await asyncio.gather(
                *get_receipt_tasks
            )

            for index, receipt_info in enumerate(receipt_list):
                error = None
                gas_price = None
                gas_used = None
                if receipt_info.error:
                    if BlockchainErrors.TX_NOT_FOUND in receipt_info.error:
                        status = EvmTransactionStatus.FAILED
                        error = receipt_info.error
                    else:
                        status = EvmTransactionStatus.PENDING
                else:
                    if receipt_info.receipt.status == 1:
                        status = EvmTransactionStatus.SUCCESS
                        gas_price = receipt_info.receipt.gas_price
                        gas_used = receipt_info.receipt.gas_used
                    else:
                        status = EvmTransactionStatus.FAILED
                        error = BlockchainErrors.TX_RECEIPT_STATUS_NOT_ONE
                tx_count += 1

                # 3. Update records
                await self.transactions_repo.update_evm_tx(
                    evm_tx_id=pending_txs[index].id,
                    update_values=UpdateEvmTransaction(
                        status=status,
                        gas_price=gas_price,
                        gas_used=gas_used,
                        error=error,
                    ),
                )

        await self.tasks_repo.delete_lock(task_id=task_id)

        self.logger.info(
            "[VerifyTransactionsTask]: Finished; processed %s transactions in %s seconds.",
            tx_count,
            round(time.time() - task_start_time, 4),
        )

    async def __get_transaction_receipt(
        self, ax_chain_id: int, tx_hash: str
    ) -> TransactionReceiptResponse:
        evm_client = self.supported_evm_clients[ax_chain_id]

        try:
            tx_receipt = await evm_client.fetch_receipt(transaction_hash=tx_hash)
            return TransactionReceiptResponse(
                receipt=tx_receipt,
                error=None,
            )
        except BlockchainClientError as e:
            return TransactionReceiptResponse(receipt=None, error=e.detail)
