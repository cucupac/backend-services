from logging import Logger
from typing import Mapping

from web3 import Web3

from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.interfaces.clients.http.bridge import IBridgeClient
from app.usecases.schemas.blockchain import (
    BlockchainClientError,
    ComputeCosts,
    TransactionHash,
)
from app.usecases.schemas.fees import MinimumFees


class EvmClient(IBlockchainClient):
    def __init__(
        self,
        bridge_client: IBridgeClient,
        chain_data: Mapping[str, str],
        logger: Logger,
    ) -> None:
        self.bridge_client = bridge_client
        self.chain_data = chain_data
        self.logger = logger

    async def update_fees(
        self, remote_data: MinimumFees, local_chain_id: str
    ) -> TransactionHash:
        """Sends transaction to the blockchain."""
        web3_client = Web3(Web3.HTTPProvider(self.chain_data[local_chain_id]["rpc"]))

        contract = web3_client.eth.contract(
            address=self.bridge_client.address,
            abi=self.bridge_client.abi,
        )

        try:
            signed_transaction = await self.bridge_client.craft_transaction(
                remote_data=remote_data,
                contract=contract,
                web3_client=web3_client,
                post_london_upgrade=self.chain_data[local_chain_id][
                    "post_london_upgrade"
                ],
            )

            return web3_client.eth.send_raw_transaction(
                transaction=signed_transaction.rawTransaction
            )
        except Exception as e:
            self.logger.error("[EvmClient]: Fee update failed: %s", e)
            raise BlockchainClientError(detail=str(e)) from e

    async def estimate_fees(self, chain_id: str) -> ComputeCosts:
        """Estimates a transaction's gas information."""

        web3_client = Web3(Web3.HTTPProvider(self.chain_data[chain_id]["rpc"]))

        contract = web3_client.eth.contract(
            address=self.bridge_client.address,
            abi=self.bridge_client.abi,
        )

        estimated_gas_units = await self.bridge_client.estimate_gas_units(
            contract=contract,
            web3_client=web3_client,
            post_london_upgrade=self.chain_data[chain_id]["post_london_upgrade"],
        )

        return ComputeCosts(
            gas_price=web3_client.eth.gas_price + web3_client.eth.max_priority_fee,
            gas_units=estimated_gas_units,
        )
