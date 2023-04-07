from logging import Logger
from typing import Mapping

from web3 import Web3

from app.usecases.interfaces.clients.http.bridge import IBridgeClient
from app.usecases.interfaces.clients.http.evm import IEvmClient
from app.usecases.schemas.blockchain import BlockchainClientError, TransactionHash


class EvmClient(IEvmClient):
    def __init__(
        self,
        bridge_client: IBridgeClient,
        chain_data: Mapping[str, str],
        logger: Logger,
    ) -> None:
        self.bridge_client = bridge_client
        self.chain_data = chain_data
        self.logger = logger

    async def deliver(self, payload: bytes, dest_chain_id: int) -> TransactionHash:
        """Sends transaction to the destination blockchain."""

        web3_client = Web3(
            Web3.HTTPProvider(self.chain_data[str(dest_chain_id)]["rpc"])
        )

        contract = web3_client.eth.contract(
            address=self.bridge_client.address,
            abi=self.bridge_client.abi,
        )

        try:
            signed_transaction = await self.bridge_client.craft_transaction(
                payload=payload,
                contract=contract,
                web3_client=web3_client,
                post_london_upgrade=self.chain_data[dest_chain_id][
                    "post_london_upgrade"
                ],
            )

            return web3_client.eth.send_raw_transaction(
                transaction=signed_transaction.rawTransaction
            )
        except Exception as e:
            self.logger.error("[EvmClient]: VAA delivery failed. Error: %s", e)
            raise BlockchainClientError(detail=str(e)) from e
