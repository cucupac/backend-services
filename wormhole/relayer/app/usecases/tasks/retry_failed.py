# pylint: disable=duplicate-code
import asyncio
import base64
import codecs
from logging import Logger

from app.settings import settings
from app.usecases.interfaces.clients.bridge import IBridgeClient
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.interfaces.services.message_processor import IVaaProcessor
from app.usecases.interfaces.tasks.retry_failed import IRetryFailedTask
from app.usecases.schemas.blockchain import BlockchainClientError, BlockchainErrors
from app.usecases.schemas.relays import (
    Status,
    UpdateJoinedRepoAdapter,
    UpdateRepoAdapter,
)


class RetryFailedTask(IRetryFailedTask):
    def __init__(  # pylint: disable = too-many-arguments
        self,
        message_processor: IVaaProcessor,
        evm_client: IEvmClient,
        bridge_client: IBridgeClient,
        relays_repo: IRelaysRepo,
        logger: Logger,
    ):
        self.vaa_processor = message_processor
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

            await asyncio.sleep(settings.retry_failed_frequency)

    async def task(self):
        """Retries non-cached, failed relays."""
        self.logger.info("[RetryFailedTask]: Task started.")

        transactions = await self.relays_repo.retrieve_failed()

        for transaction in transactions:
            if not transaction.relay_message:
                # The VAA is unknown to our system.

                # 1. Get VAA from Wormhole
                message = await self.bridge_client.fetch_bridge_message(
                    emitter_address=transaction.emitter_address,
                    emitter_chain_id=transaction.source_chain_id,
                    sequence=transaction.sequence,
                )

                message_bytes = base64.b64decode(message.b64_message)
                parsed_vaa = self.vaa_processor.parse_vaa(vaa=message_bytes)
                message_hex = codecs.encode(message_bytes, "hex_codec").decode().upper()

                # 2. Deliver message
                try:
                    transaction_hash_bytes = await self.evm_client.deliver(
                        payload=message_hex,
                        dest_chain_id=parsed_vaa.payload.dest_chain_id,
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
                await self.relays_repo.update_relay_and_transaction(
                    update_data=UpdateJoinedRepoAdapter(
                        emitter_address=transaction.emitter_address,
                        source_chain_id=transaction.source_chain_id,
                        sequence=transaction.sequence,
                        transaction_hash=transaction_hash,
                        error=error,
                        status=status,
                        from_address=parsed_vaa.payload.from_address,
                        to_address=f"0x{parsed_vaa.payload.to_address:040x}",
                        dest_chain_id=parsed_vaa.payload.dest_chain_id,
                        amount=parsed_vaa.payload.amount,
                        message=message_hex,
                    )
                )
            else:
                # The VAA is known to our system; it just needs to be retried.
                try:
                    transaction_hash_bytes = await self.evm_client.deliver(
                        vaa=transaction.relay_message,
                        dest_chain_id=transaction.dest_chain_id,
                    )
                except BlockchainClientError as e:
                    if BlockchainErrors.MESSAGE_PROCESSED in e.detail:
                        error = None
                        status = Status.SUCCESS
                        transaction_hash = None
                    else:
                        error = e.detail
                        status = Status.FAILED
                        transaction_hash = None
                else:
                    error = None
                    status = Status.SUCCESS
                    transaction_hash = transaction_hash_bytes.hex()

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

        self.logger.info("[RetryFailedTask]: Finished; sleeping now...")
