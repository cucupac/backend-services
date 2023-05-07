import asyncio
import base64
import codecs
from logging import Logger

from app.dependencies import CHAIN_ID_LOOKUP
from app.settings import settings
from app.usecases.interfaces.clients.bridge import IBridgeClient
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.interfaces.services.message_processor import IVaaProcessor
from app.usecases.interfaces.tasks.gather_missed import IGatherMissedVaasTask
from app.usecases.schemas.bridge import BridgeClientException, NotFoundException
from app.usecases.schemas.relays import CacheStatus, GrpcStatus, RelayErrors, Status
from app.usecases.schemas.transactions import CreateRepoAdapter


class GatherMissedVaasTask(IGatherMissedVaasTask):
    def __init__(
        self,
        message_processor: IVaaProcessor,
        bridge_client: IBridgeClient,
        relays_repo: IRelaysRepo,
        logger: Logger,
    ):
        self.message_processor = message_processor
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

            await asyncio.sleep(settings.gather_missed_frequency)

    async def task(self):
        """Retries untracked transactions."""
        self.logger.info("[GatherMissedVaasTask]: Task started.")

        # Get missed transactions
        for wh_chain_id in CHAIN_ID_LOOKUP.keys():
            transaction = await self.relays_repo.get_latest_sequence(
                emitter_address=settings.evm_wormhole_bridge,
                source_chain_id=wh_chain_id,
            )

            if transaction is not None:
                new_sequence = transaction.sequence + 1

                while True:
                    # 1. Fetch message
                    try:
                        message = await self.bridge_client.fetch_bridge_message(
                            emitter_address=transaction.emitter_address,
                            emitter_chain_id=transaction.source_chain_id,
                            sequence=new_sequence,
                        )
                    except (
                        BridgeClientException,
                        NotFoundException,
                    ) as e:
                        if isinstance(e, NotFoundException):
                            self.logger.info(
                                "[GatherMissedVaasTask]: Reached point of no new messages for chain id: %s.",
                                wh_chain_id,
                            )
                        else:
                            self.logger.error(
                                "[GatherMissedVaasTask]: Unexpected error: %s", e
                            )
                        break
                    else:
                        message_bytes = base64.b64decode(message.b64_message)
                        parsed_vaa = self.message_processor.parse_vaa(vaa=message_bytes)
                        message_hex = codecs.encode(message_bytes, "hex_codec").decode()

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

                    new_sequence += 1

        self.logger.info("[GatherMissedVaasTask]: Finished; sleeping now...")
