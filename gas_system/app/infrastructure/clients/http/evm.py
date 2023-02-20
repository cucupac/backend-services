from logging import Logger
from typing import Any, List, Mapping

from eth_account.datastructures import SignedTransaction
from web3 import Web3
from web3.contract import Contract

from app.settings import settings
from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.schemas.blockchain import (
    BlockchainClientError,
    ComputeCosts,
    TransactionHash,
)
from app.usecases.schemas.fees import MinimumFees


class EvmClient(IBlockchainClient):
    def __init__(
        self,
        abi: List[Mapping[str, Any]],
        chain_lookup: Mapping[str, str],
        mock_set_send_fees_params: MinimumFees,
        logger: Logger,
    ) -> None:
        self.abi = abi
        self.chain_lookup = chain_lookup
        self.logger = logger
        self.mock_set_send_fees_params = mock_set_send_fees_params

    async def update_fees(
        self, remote_data: MinimumFees, local_chain_id: str
    ) -> TransactionHash:
        """Sends transaction to the blockchain."""

        web3_client = Web3(Web3.HTTPProvider(self.chain_lookup[local_chain_id]["rpc"]))

        contract = web3_client.eth.contract(
            address=self.chain_lookup[str(local_chain_id)]["bridge_contract"],
            abi=self.abi,
        )

        try:
            signed_transaction = await self.__craft_transaction(
                data=remote_data, contract=contract, web3_client=web3_client
            )

            return web3_client.eth.send_raw_transaction(
                transaction=signed_transaction.rawTransaction
            )
        except Exception as e:
            self.logger.error("[EvmClient]: Fee update failed: %s", e)
            raise BlockchainClientError(detail=str(e)) from e

    async def __craft_transaction(
        self, remote_data: MinimumFees, contract: Contract, web3_client: Web3
    ) -> SignedTransaction:
        """Craft a raw transaction to be sent to the blockchain."""

        max_priority_fee = web3_client.eth.max_priority_fee
        gas_price_estimate = web3_client.eth.gas_price

        transaction = contract.functions.setSendFees(
            remote_data.remote_chain_ids, remote_data.fees
        ).buildTransaction(
            {
                "from": settings.admin_address,
                "nonce": web3_client.eth.get_transaction_count(settings.admin_address),
                "maxFeePerGas": gas_price_estimate + max_priority_fee,
                "maxPriorityFeePerGas": max_priority_fee,
            }
        )

        return web3_client.eth.account.sign_transaction(
            transaction_dict=transaction, private_key=settings.admin_private_key
        )

    async def estimate_fees(self, chain_id: str) -> ComputeCosts:
        """Estimates a transaction's gas information."""

        web3_client = Web3(Web3.HTTPProvider(self.chain_lookup[chain_id]["rpc"]))

        contract = web3_client.eth.contract(
            address=self.chain_lookup[chain_id]["bridge_contract"],
            abi=self.abi,
        )

        # TODO: This estimatio uses mock fee vlaues. Ensure gas unit estimation is accurate.
        estimated_gas_units = contract.functions.setSendFees(
            self.mock_set_send_fees_params.remote_chain_ids,
            self.mock_set_send_fees_params.fees,
        ).estimate_gas()

        return ComputeCosts(
            gas_price=web3_client.eth.gas_price + web3_client.eth.max_priority_fee,
            gas_units=estimated_gas_units,
        )
