import asyncio
from logging import Logger
from typing import List

from app.settings import settings
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.interfaces.tasks.verify_delivery import IVerifyDeliveryTask
from app.usecases.schemas.blockchain import (
    BlockchainClientError,
    BlockchainErrors,
    TransactionReceipt,
    TransactionReceiptResponse,
)
from app.usecases.schemas.relays import Status, UpdateRepoAdapter


class VerifyDeliveryTask(IVerifyDeliveryTask):
    def __init__(
        self, evm_client: IEvmClient, relays_repo: IRelaysRepo, logger: Logger
    ):
        self.evm_client = evm_client
        self.relays_repo = relays_repo
        self.logger = logger

    async def start_task(self) -> None:
        """Starts automated task to periodically verify that submitted transactions were, in fact, delivered."""
        while True:
            try:
                await self.task()
            except asyncio.CancelledError:  # pylint: disable = try-except-raise
                raise
            except Exception as e:  # pylint: disable = broad-except
                self.logger.exception(e)

            await asyncio.sleep(settings.verify_delivery_frequency)

    async def task(self) -> None:
        """Verify the delivery status of submitted transactions."""
        self.logger.info("[VerifyDeliveryTask]: Started.")

        undelivered_transactions = await self.relays_repo.retrieve_undelivered()

        get_receipt_tasks = [
            asyncio.create_task(self.__get_transaction_receipt(transaction=transaction))
            for transaction in undelivered_transactions
        ]

        receipt_list: List[TransactionReceiptResponse] = await asyncio.gather(
            *get_receipt_tasks
        )

        for index, receipt_info in enumerate(receipt_list):
            if receipt_info.error:
                if BlockchainErrors.TX_HASH_NOT_IN_CHAIN in receipt_info.error:
                    status = Status.FAILED
                    error = BlockchainErrors.TX_HASH_NOT_IN_CHAIN
                else:
                    status = Status.PENDING
                    error = None
            else:
                if receipt_info.receipt.status == 1:
                    status = Status.SUCCESS
                    error = None
                else:
                    status = Status.FAILED
                    error = BlockchainErrors.TX_RECEIPT_STATUS_NOT_ONE

            # Update records
            await self.relays_repo.update(
                relay=UpdateRepoAdapter(
                    emitter_address=undelivered_transactions[index].emitter_address,
                    source_chain_id=undelivered_transactions[index].source_chain_id,
                    sequence=undelivered_transactions[index].sequence,
                    status=status,
                    error=error,
                )
            )

        self.logger.info(
            "[VerifyDeliveryTask]: Finished; processed %s transactions.",
            len(undelivered_transactions),
        )

    async def __get_transaction_receipt(
        self, transaction
    ) -> TransactionReceiptResponse:
        try:
            transaction_receipt = await self.evm_client.fetch_receipt(
                transaction_hash=transaction.relay_transaction_hash,
                dest_chain_id=transaction.dest_chain_id,
            )
            return TransactionReceiptResponse(
                receipt=TransactionReceipt(status=transaction_receipt.status),
                error=None,
            )
        except BlockchainClientError as e:
            return TransactionReceiptResponse(receipt=None, error=e.detail)
