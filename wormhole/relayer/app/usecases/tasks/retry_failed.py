# pylint: disable=duplicate-code,too-many-arguments
import asyncio
import base64
import codecs
import time
from collections import defaultdict
from logging import Logger
from typing import List, Mapping, Optional, Union

from app.dependencies import CHAIN_ID_LOOKUP
from app.settings import settings
from app.usecases.interfaces.clients.bridge import IBridgeClient
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.interfaces.repos.tasks import ITasksRepo
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
from app.usecases.schemas.tasks import TaskName
from app.usecases.schemas.transactions import TransactionsJoinRelays
from app.usecases.schemas.vaa import ExternalVaa


class RetryFailedTask(IRetryFailedTask):
    def __init__(
        self,
        message_processor: IVaaProcessor,
        supported_evm_clients: Mapping[int, IEvmClient],
        bridge_client: IBridgeClient,
        relays_repo: IRelaysRepo,
        tasks_repo: ITasksRepo,
        logger: Logger,
    ):
        self.vaa_processor = message_processor
        self.supported_evm_clients = supported_evm_clients
        self.bridge_client = bridge_client
        self.relays_repo = relays_repo
        self.tasks_repo = tasks_repo
        self.logger = logger
        self.name = TaskName.RETRY_FAILED

    async def start_task(self) -> None:
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

        # Check distributed lock for task availability.
        task = await self.tasks_repo.retrieve(task_name=self.name)
        available_task = await self.tasks_repo.create_lock(task_id=task.id)
        if not available_task:
            self.logger.info("[RetryFailedTask]: Encountered lock; stopping work.")
            return

        task_start_time = time.time()

        failed_relays = await self.relays_repo.retrieve_failed()

        # Contstruct same-destination-chain "concurrency sets"; a none set can exist if no destination chain ID.
        dest_chain_id_groups = defaultdict(list)
        for relay in failed_relays:
            dest_chain_id_groups[relay.dest_chain_id].append(relay)

        # Asynchronously retrieve transaction information for all in none set
        bridge_message_tasks = [
            asyncio.create_task(
                self.__get_bridge_message(
                    emitter_address=relay.emitter_address,
                    emitter_chain_id=relay.source_chain_id,
                    sequence=relay.sequence,
                )
            )
            for relay in dest_chain_id_groups[None]
        ]
        externally_obtained_vaas: List[ExternalVaa] = await asyncio.gather(
            *bridge_message_tasks
        )

        # Add externally obtained vaas to "concurrency sets"
        for vaa in externally_obtained_vaas:
            if vaa:
                dest_chain_id_groups[vaa.parsed_vaa.payload.dest_chain_id].append(vaa)

        # Asynchronously execute relays, grouped by destination chain, for throughput efficiency gains
        relay_tasks = []
        for dest_chain_id, relays in dest_chain_id_groups.items():
            if dest_chain_id:
                chain_id = CHAIN_ID_LOOKUP[dest_chain_id]
                dest_evm_client = self.supported_evm_clients[chain_id]
                current_nonce = await dest_evm_client.get_current_nonce()
                relay_tasks.append(
                    asyncio.create_task(
                        self.__execute_relays(
                            relays=relays, current_nonce=current_nonce
                        )
                    )
                )

        await asyncio.gather(*relay_tasks)

        await self.tasks_repo.delete_lock(task_id=task.id)

        self.logger.info(
            "[RetryFailedTask]: Finished; processed %s transactions in %s seconds.",
            len(failed_relays),
            time.time() - task_start_time,
        )

    async def __execute_relays(
        self,
        relays: List[Union[TransactionsJoinRelays, ExternalVaa]],
        current_nonce: int,
    ) -> None:
        """This function executes same-destination-chain relays synchronously."""

        for relay in relays:
            if isinstance(relay, ExternalVaa):
                # NOTE: The VAA is unknown to our system.
                submitted_relay = await self.__submit_relay(
                    payload=bytes.fromhex(relay.message_hex),
                    source_chain_id=relay.parsed_vaa.emitter_chain,
                    sequence=relay.parsed_vaa.sequence,
                    dest_chain_id=relay.parsed_vaa.payload.dest_chain_id,
                    nonce=current_nonce,
                )
                await self.__update_database(
                    relay=relay, submitted_relay=submitted_relay, external_vaa=relay
                )
            else:
                # NOTE: The VAA is already known to our system.
                submitted_relay = await self.__submit_relay(
                    payload=bytes.fromhex(relay.relay_message),
                    source_chain_id=relay.source_chain_id,
                    sequence=relay.sequence,
                    dest_chain_id=relay.dest_chain_id,
                    nonce=current_nonce,
                )
                await self.__update_database(
                    relay=relay, submitted_relay=submitted_relay
                )

            current_nonce += 1

    async def __get_bridge_message(
        self, emitter_address: str, emitter_chain_id: int, sequence: int
    ) -> ExternalVaa:
        try:
            message = await self.bridge_client.fetch_bridge_message(
                emitter_address=emitter_address,
                emitter_chain_id=emitter_chain_id,
                sequence=sequence,
            )
        except BridgeClientException as e:
            self.logger.error("[RetryFailedTask]: Unexpected error: %s", e)
            return None

        message_bytes = base64.b64decode(message.b64_message)
        parsed_vaa = self.vaa_processor.parse_vaa(vaa=message_bytes)
        message_hex = codecs.encode(message_bytes, "hex_codec").decode().upper()
        return ExternalVaa(parsed_vaa=parsed_vaa, message_hex=message_hex)

    async def __submit_relay(
        self,
        payload: bytes,
        source_chain_id: int,
        sequence: int,
        dest_chain_id: int,
        nonce: int,
    ) -> SubmittedRelay:
        # The VAA is known to our system; it just needs to be retried.
        chain_id = CHAIN_ID_LOOKUP[dest_chain_id]
        dest_evm_client = self.supported_evm_clients[chain_id]

        try:
            transaction_hash_bytes = await dest_evm_client.deliver(
                payload=payload,
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
        relay: TransactionsJoinRelays,
        submitted_relay: SubmittedRelay,
        external_vaa: Optional[ExternalVaa] = None,
    ) -> None:
        """This internal function updates transcation and relay records in the database.
        The method by which it updates is dependent on whether or not the vaa was obtained externally.
        """

        if external_vaa:
            await self.relays_repo.update_relay_and_transaction(
                update_data=UpdateJoinedRepoAdapter(
                    emitter_address=external_vaa.parsed_vaa.emitter_address,
                    source_chain_id=external_vaa.parsed_vaa.emitter_chain,
                    sequence=external_vaa.parsed_vaa.sequence,
                    from_address=external_vaa.parsed_vaa.payload.from_address,
                    to_address=f"0x{external_vaa.parsed_vaa.payload.to_address:040x}",
                    dest_chain_id=external_vaa.parsed_vaa.payload.dest_chain_id,
                    amount=external_vaa.parsed_vaa.payload.amount,
                    message=external_vaa.message_hex,
                    transaction_hash=submitted_relay.transaction_hash,
                    error=submitted_relay.error,
                    status=submitted_relay.status,
                )
            )
        else:
            await self.relays_repo.update(
                relay=UpdateRepoAdapter(
                    emitter_address=relay.emitter_address,
                    source_chain_id=relay.source_chain_id,
                    sequence=relay.sequence,
                    transaction_hash=submitted_relay.transaction_hash,
                    error=submitted_relay.error,
                    status=submitted_relay.status,
                )
            )
