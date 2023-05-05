import base64
import asyncio
from logging import Logger

from app.usecases.interfaces.tasks.retry_queued import IRetryQueuedTask
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.interfaces.clients.bridge import IBridgeClient
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.schemas.relays import Status
from app.usecases.schemas.relays import UpdateRepoAdapter
from app.usecases.schemas.blockchain import BlockchainClientError
from app.settings import settings


class RetryUnqueuedTask(IRetryQueuedTask):
    def __init__(
        self,
        evm_client: IEvmClient,
        bridge_client: IBridgeClient,
        relays_repo: IRelaysRepo,
        logger: Logger,
    ):
        self.evm_client = evm_client
        self.bridge_client = bridge_client
        self.relays_repo = relays_repo
        self.logger = logger

    async def start_task(self) -> None:
        """Starts automated task to periodically check for previously unsuccessful queued messages."""
        while True:
            try:
                await self.task()
            except asyncio.CancelledError:  # pylint: disable = try-except-raise
                raise
            except Exception as e:  # pylint: disable = broad-except
                self.logger.exception(e)

            await asyncio.sleep(settings.retry_unqueued_frequency)

    async def task(self):
        """Retries untracked transactions."""
        self.logger.info("[RetryUnqueuedTask]: Task started.")

        # Get missed transactions

        for transaction in transactions:
            # 1. Get bridge message from cross-chain message protocol provider
            b64_encoded_message = await self.bridge_client.fetch_bridge_message(
                emitter_address=transaction.emitter_address,
                sequence=transaction.sequence,
            )

            message_bytes = base64.b64decode(b64_encoded_message)

            # 2. Retry transaction
            try:
                transaction_hash_bytes = await self.evm_client.deliver(
                    vaa=message_bytes, dest_chain_id=transaction.dest_chain_id
                )
            except BlockchainClientError as e:
                error = e.detail
                status = Status.FAILED
                transaction_hash = None
            else:
                error = None
                status = Status.SUCCESS
                transaction_hash = transaction_hash_bytes.hex()

            # 3. Update database
            await self.relays_repo.update(
                relay=UpdateRepoAdapter(
                    emitter_address=transaction.emitter_address,
                    source_chain_id=transaction.source_chain_id,
                    sequence=transaction.sequence,
                    transaction_hash=transaction_hash,
                    error=error,
                    status=status,
                )
            )

        self.logger.info("[RetryUnqueuedTask]: Sleeping now...")
