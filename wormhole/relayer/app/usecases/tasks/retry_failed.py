# pylint: disable=duplicate-code
import asyncio
import base64
import codecs
import time
from collections import defaultdict
from logging import Logger
from typing import List, Optional

from app.settings import settings
from app.usecases.interfaces.clients.bridge import IBridgeClient
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.interfaces.services.message_processor import IVaaProcessor
from app.usecases.interfaces.tasks.retry_failed import IRetryFailedTask
from app.usecases.schemas.blockchain import BlockchainClientError, BlockchainErrors
from app.usecases.schemas.bridge import BridgeClientException
from app.usecases.schemas.relays import (
    Status,
    SubmittedRelay,
    UpdateJoinedRepoAdapter,
    UpdateRepoAdapter,
)
from app.usecases.schemas.transactions import TransactionsJoinRelays
from app.usecases.schemas.vaa import ParsedVaa


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

    async def task(self) -> None:
        """Retries non-cached, failed relays."""
        self.logger.info("[RetryFailedTask]: Started.")
        task_start_time = time.time()

        failed_transactions = await self.relays_repo.retrieve_failed()

        # Contstruct same-destination-chain "concurrency sets"
        dest_chain_id_groups = defaultdict(list)
        for transaction in failed_transactions:
            dest_chain_id_groups[transaction.dest_chain_id].append(transaction)

        # Impose asynchronicity, delinated by destination chains, for efficiency gains
        relay_tasks = []
        for dest_chain_id, transactions in dest_chain_id_groups.items():
            current_nonce = await self.evm_client.get_current_nonce(
                dest_chain_id=dest_chain_id
            )
            relay_tasks.append(
                asyncio.create_task(
                    self.__execute_relays(
                        transactions=transactions, current_nonce=current_nonce
                    )
                )
            )

        await asyncio.gather(*relay_tasks)

        self.logger.info(
            "[RetryFailedTask]: Finished; processed %s transactions in %s seconds.",
            len(failed_transactions),
            time.time() - task_start_time,
        )

    async def __execute_relays(
        self, transactions: List[TransactionsJoinRelays], current_nonce: int
    ) -> None:
        """This function executes same-destination-chain relays synchronously."""

        # message_bytes_list is in the same order as transactions, per asyncio.gather's return order
        bridge_message_tasks = [
            asyncio.create_task(
                self.__get_bridge_message(
                    emitter_address=transaction.emitter_address,
                    emitter_chain_id=transaction.source_chain_id,
                    sequence=transaction.sequence,
                )
            )
            for transaction in transactions
        ]
        message_bytes_list = await asyncio.gather(*bridge_message_tasks)

        for index, transaction in enumerate(transactions):
            if not transaction.relay_message:
                # The VAA is unknown to our system.

                message_bytes = message_bytes_list[index]
                if message_bytes is not None:
                    parsed_vaa = self.vaa_processor.parse_vaa(vaa=message_bytes)
                    message_hex = (
                        codecs.encode(message_bytes, "hex_codec").decode().upper()
                    )

                    submitted_relay = await self.__submit_relay(
                        payload=message_hex,
                        source_chain_id=transaction.source_chain_id,
                        sequence=transaction.sequence,
                        dest_chain_id=parsed_vaa.payload.dest_chain_id,
                        nonce=current_nonce,
                    )
                    await self.__update_database(
                        transaction=transaction,
                        submitted_relay=submitted_relay,
                        parsed_vaa=parsed_vaa,
                        message_hex=message_hex,
                    )
            else:
                submitted_relay = await self.__submit_relay(
                    payload=transaction.relay_message,
                    source_chain_id=transaction.source_chain_id,
                    sequence=transaction.sequence,
                    dest_chain_id=transaction.dest_chain_id,
                    nonce=current_nonce,
                )
                await self.__update_database(
                    transaction=transaction, submitted_relay=submitted_relay
                )

            current_nonce += 1

    async def __get_bridge_message(
        self, emitter_address: str, emitter_chain_id: int, sequence: int
    ) -> bytes:
        try:
            message = await self.bridge_client.fetch_bridge_message(
                emitter_address=emitter_address,
                emitter_chain_id=emitter_chain_id,
                sequence=sequence,
            )
            return base64.b64decode(message.b64_message)
        except BridgeClientException as e:
            self.logger.error(
                "[RetryFailedTask]: Unexpected error in get_bridge_message(): %s", e
            )
            return None

    async def __submit_relay(
        self,
        payload: str,
        source_chain_id: int,
        sequence: int,
        dest_chain_id: int,
        nonce: int,
    ) -> SubmittedRelay:
        # The VAA is known to our system; it just needs to be retried.
        try:
            transaction_hash_bytes = await self.evm_client.deliver(
                payload=payload,
                dest_chain_id=dest_chain_id,
                nonce=nonce,
            )
        except BlockchainClientError as e:
            self.logger.info(
                "[RetryFailedTask]: VAA delivery failed; chain id %s, sequence %s",
                source_chain_id,
                sequence,
            )
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
            # A success is constituted by transaction receipt status of 1
            status = Status.PENDING
            transaction_hash = transaction_hash_bytes.hex()
            self.logger.info(
                "[RetryFailedTask]: Transaction submission successful; chain id: %s, sequence: %s, transaction hash: %s",
                source_chain_id,
                sequence,
                transaction_hash,
            )

        return SubmittedRelay(
            error=error, status=status, transaction_hash=transaction_hash
        )

    async def __update_database(
        self,
        transaction: TransactionsJoinRelays,
        submitted_relay: SubmittedRelay,
        parsed_vaa: Optional[ParsedVaa] = None,
        message_hex: Optional[str] = None,
    ) -> None:
        if parsed_vaa:
            await self.relays_repo.update_relay_and_transaction(
                update_data=UpdateJoinedRepoAdapter(
                    emitter_address=transaction.emitter_address,
                    source_chain_id=transaction.source_chain_id,
                    sequence=transaction.sequence,
                    transaction_hash=submitted_relay.transaction_hash,
                    error=submitted_relay.error,
                    status=submitted_relay.status,
                    from_address=parsed_vaa.payload.from_address,
                    to_address=f"0x{parsed_vaa.payload.to_address:040x}",
                    dest_chain_id=parsed_vaa.payload.dest_chain_id,
                    amount=parsed_vaa.payload.amount,
                    message=message_hex,
                )
            )
        else:
            await self.relays_repo.update(
                relay=UpdateRepoAdapter(
                    emitter_address=transaction.emitter_address,
                    source_chain_id=transaction.source_chain_id,
                    sequence=transaction.sequence,
                    transaction_hash=submitted_relay.transaction_hash,
                    error=submitted_relay.error,
                    status=submitted_relay.status,
                )
            )
