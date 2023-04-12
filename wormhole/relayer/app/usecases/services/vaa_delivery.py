import json

from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.interfaces.clients.websocket import IWebsocketClient
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.interfaces.services.vaa_delivery import IVaaDelivery
from app.usecases.schemas.blockchain import BlockchainClientError
from app.usecases.schemas.relays import Status, UpdateRepoAdapter
from app.usecases.schemas.unique_set import UniqueSetMessage


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

    async def process(self, set_message: bytes) -> None:
        """Process message from unique set."""

        message = UniqueSetMessage(**json.loads(set_message.decode()))

        # Send Vaa to destination chain
        try:
            transaction_hash_bytes = await self.evm_client.deliver(
                payload=bytes.fromhex(message.vaa_hex),
                dest_chain_id=message.dest_chain_id,
            )
        except BlockchainClientError as e:
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
