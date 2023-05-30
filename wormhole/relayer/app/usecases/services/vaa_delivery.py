import json
from typing import Mapping
from logging import Logger

from app.dependencies import CHAIN_ID_LOOKUP
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.interfaces.clients.websocket import IWebsocketClient
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.interfaces.services.vaa_delivery import IVaaDelivery
from app.usecases.schemas.blockchain import BlockchainClientError, BlockchainErrors
from app.usecases.schemas.relays import Status, UpdateRepoAdapter
from app.usecases.schemas.unique_set import UniqueSetMessage


class VaaDelivery(IVaaDelivery):
    def __init__(
        self,
        relays_repo: IRelaysRepo,
        supported_evm_clients: Mapping[int, IEvmClient],
        websocket_client: IWebsocketClient,
        logger: Logger,
    ):
        self.relays_repo = relays_repo
        self.supported_evm_clients = supported_evm_clients
        self.websocket_client = websocket_client
        self.logger = logger

    async def process(self, set_message: bytes) -> None:
        """Process message from unique set."""

        message = UniqueSetMessage(**json.loads(set_message.decode()))

        # Send Vaa to destination chain
        chain_id = CHAIN_ID_LOOKUP[message.dest_chain_id]
        dest_evm_client = self.supported_evm_clients[chain_id]
        try:
            transaction_hash_bytes = await dest_evm_client.deliver(
                payload=message.vaa_hex
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
            # A success is constituted by transaction receipt status of 1
            status = Status.PENDING
            transaction_hash = transaction_hash_bytes.hex()
            self.logger.info(
                "[VaaDelivery]: Transaction submission successful; chain id: %s, sequence: %s, transaction hash: %s",
                message.emitter_chain,
                message.sequence,
                transaction_hash,
            )

        # Notify client via web socket
        await self.websocket_client.notify_client(
            address=message.from_address,
            status=status,
            error=error,
            transaction_hash=transaction_hash,
        )

        # Update relay in the database
        await self.relays_repo.update(
            relay=UpdateRepoAdapter(
                emitter_address=message.emitter_address,
                source_chain_id=message.emitter_chain,
                sequence=message.sequence,
                transaction_hash=transaction_hash,
                error=error,
                status=status,
            )
        )
