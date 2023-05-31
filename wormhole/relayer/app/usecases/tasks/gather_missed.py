# pylint: disable=duplicate-code
import asyncio
import base64
import codecs
from logging import Logger

from app.dependencies import CHAIN_ID_LOOKUP
from app.settings import settings
from app.usecases.interfaces.clients.bridge import IBridgeClient
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.interfaces.services.message_processor import IVaaProcessor
from app.usecases.interfaces.tasks.gather_missed import IGatherMissedVaasTask
from app.usecases.schemas.bridge import BridgeClientException, NotFoundException
from app.usecases.schemas.relays import CacheStatus, GrpcStatus, RelayErrors, Status
from app.usecases.schemas.tasks import TaskName
from app.usecases.schemas.transactions import CreateRepoAdapter


class GatherMissedVaasTask(IGatherMissedVaasTask):
    def __init__(  # pylint: disable = too-many-arguments
        self,
        message_processor: IVaaProcessor,
        bridge_client: IBridgeClient,
        tasks_repo: ITasksRepo,
        relays_repo: IRelaysRepo,
        logger: Logger,
    ):
        self.message_processor = message_processor
        self.bridge_client = bridge_client
        self.relays_repo = relays_repo
        self.tasks_repo = tasks_repo
        self.logger = logger
        self.name = TaskName.GATHER_MISSED

    async def start_task(self) -> None:
        while True:
            try:
                await self.task()
            except asyncio.CancelledError:  # pylint: disable = try-except-raise
                raise
            except Exception as e:  # pylint: disable = broad-except
                self.logger.exception(e)

            await asyncio.sleep(settings.gather_missed_frequency)

    async def task(self) -> None:
        """Gathers untracked transactions."""

        self.logger.info("[GatherMissedVaasTask]: Started.")

        # Check distributed lock for task availability.
        task = await self.tasks_repo.retrieve(task_name=self.name)
        available_task = await self.tasks_repo.create_lock(task_id=task.id)
        if not available_task:
            self.logger.info("[GatherMissedVaasTask]: Encountered lock; stopping work.")
            return

        # Get missed transactions
        for wh_chain_id in CHAIN_ID_LOOKUP:
            transaction = await self.relays_repo.get_latest_sequence(
                emitter_address=settings.evm_wormhole_bridge,
                source_chain_id=wh_chain_id,
            )

            if transaction is not None:
                new_sequence = transaction.sequence + 1
            else:
                new_sequence = 0

            while True:
                # 1. Fetch message
                try:
                    message = await self.bridge_client.fetch_bridge_message(
                        emitter_address=settings.evm_wormhole_bridge,
                        emitter_chain_id=wh_chain_id,
                        sequence=new_sequence,
                    )
                except (
                    BridgeClientException,
                    NotFoundException,
                ) as e:
                    if isinstance(e, NotFoundException):
                        self.logger.info(
                            "[GatherMissedVaasTask]: Reached point of no new messages; chain id: %s, sequence: %s",
                            wh_chain_id,
                            new_sequence,
                        )
                    else:
                        self.logger.error(
                            "[GatherMissedVaasTask]: Unexpected error: %s", e
                        )
                    break
                else:
                    message_bytes = base64.b64decode(message.b64_message)
                    parsed_vaa = self.message_processor.parse_vaa(vaa=message_bytes)
                    message_hex = (
                        codecs.encode(message_bytes, "hex_codec").decode().upper()
                    )

                    # 2. Store record as failed (another task will pick it up)
                    await self.relays_repo.create(
                        transaction=CreateRepoAdapter(
                            emitter_address=parsed_vaa.emitter_address,
                            from_address=parsed_vaa.payload.from_address,
                            to_address=f"0x{parsed_vaa.payload.to_address:040x}",
                            source_chain_id=parsed_vaa.emitter_chain,
                            dest_chain_id=parsed_vaa.payload.dest_chain_id,
                            amount=parsed_vaa.payload.amount,
                            sequence=parsed_vaa.sequence,
                            relay_error=RelayErrors.MISSED_VAA,
                            relay_status=Status.FAILED,
                            relay_message=message_hex,
                            relay_cache_status=CacheStatus.NEVER_CACHED,
                            relay_grpc_status=GrpcStatus.FAILED,
                        )
                    )

                    self.logger.info(
                        "[GatherMissedVaasTask]: Retrieved missed VAA; chain id: %s, sequence: %s",
                        parsed_vaa.emitter_chain,
                        parsed_vaa.sequence,
                    )

                new_sequence += 1

        await self.tasks_repo.delete_lock(task_id=task.id)

        self.logger.info("[GatherMissedVaasTask]: Finished; sleeping now...")
