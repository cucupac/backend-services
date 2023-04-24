from logging import Logger
from typing import Any, List, Mapping

from eth_account.datastructures import SignedTransaction
from web3 import Web3
from web3.contract import Contract

from app.dependencies import CHAIN_ID_LOOKUP
from app.settings import settings
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.schemas.blockchain import BlockchainClientError, TransactionHash


class EvmClient(IEvmClient):
    def __init__(
        self,
        abi: List[Mapping[str, Any]],
        chain_data: Mapping[str, str],
        logger: Logger,
    ) -> None:
        self.abi = abi
        self.chain_data = chain_data
        self.logger = logger

    async def deliver(self, payload: bytes, dest_chain_id: int) -> TransactionHash:
        """Sends transaction to the destination blockchain."""
        web3_client = Web3(
            Web3.HTTPProvider(self.chain_data[CHAIN_ID_LOOKUP[dest_chain_id]]["rpc"])
        )

        contract = web3_client.eth.contract(
            address=settings.evm_wormhole_bridge,
            abi=self.abi,
        )

        try:
            signed_transaction = await self.__craft_transaction(
                payload=payload,
                contract=contract,
                web3_client=web3_client,
                post_london_upgrade=self.chain_data[CHAIN_ID_LOOKUP[dest_chain_id]][
                    "post_london_upgrade"
                ],
            )
            return web3_client.eth.send_raw_transaction(
                transaction=signed_transaction.rawTransaction
            )
        except Exception as e:
            self.logger.error("[EvmClient]: VAA delivery failed. Error: %s", e)
            raise BlockchainClientError(detail=str(e)) from e

    async def __craft_transaction(
        self,
        payload: bytes,
        contract: Contract,
        web3_client: Web3,
        post_london_upgrade: bool,
    ) -> SignedTransaction:
        """Craft a raw transaction to be sent to the blockchain."""
        transaction_builder = {
            "from": settings.relayer_address,
            "nonce": web3_client.eth.get_transaction_count(settings.relayer_address),
        }

        gas_price_estimate = web3_client.eth.gas_price

        if post_london_upgrade:
            max_priority_fee = web3_client.eth.max_priority_fee
            transaction_builder["maxFeePerGas"] = gas_price_estimate + max_priority_fee
            transaction_builder["maxPriorityFeePerGas"] = max_priority_fee
        else:
            transaction_builder["gasPrice"] = gas_price_estimate

        transaction = contract.functions.processMessage(payload).buildTransaction(
            transaction_builder
        )

        return web3_client.eth.account.sign_transaction(
            transaction_dict=transaction, private_key=settings.relayer_private_key
        )
