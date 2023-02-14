import json

from app.usecases.interfaces.clients.http.evm import IEvmClient
from app.usecases.interfaces.clients.ws.websocket import IWebsocketClient
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.interfaces.services.vaa_delivery import IVaaDelivery
from app.usecases.schemas.evm import EvmClientError
from app.usecases.schemas.queue import QueueMessage
from app.usecases.schemas.relays import Status, UpdateRepoAdapter


class VaaDelivery(IVaaDelivery):
    def __init__(
        self,
        relays_repo: IRelaysRepo,
        evm_client: IEvmClient,
        websocket_client: IWebsocketClient,
    ):
        self.relays_repo = relays_repo
        self.evm_client = evm_client
        self.websocket_client = websocket_client

    async def process(self, queue_message: bytes) -> None:
        """Process message from queue."""

        message = QueueMessage(**json.loads(queue_message.decode()))

        # Send Vaa to destination chain
        try:
            transaction_hash_bytes = await self.evm_client.deliver(
                vaa=bytes.fromhex(message.vaa_hex), dest_chain_id=message.dest_chain_id
            )
        except EvmClientError as e:
            error = e.detail
            status = Status.FAILED
            transaction_hash = None
        else:
            error = None
            status = Status.SUCCESS
            transaction_hash = transaction_hash_bytes.hex()

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