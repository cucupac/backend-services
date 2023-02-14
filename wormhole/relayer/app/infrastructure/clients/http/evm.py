import base64
import json
from logging import Logger
from typing import Any, List, Mapping

from eth_account.datastructures import SignedTransaction
from web3 import Web3
from web3.contract import Contract

from app.settings import settings
from app.usecases.interfaces.clients.http.evm import IEvmClient
from app.usecases.schemas.evm import EvmClientError, TransactionHash


class EvmClient(IEvmClient):
    def __init__(self, abi: List[Mapping[str, Any]], logger: Logger) -> None:
        self.abi = abi
        self.logger = logger

    async def deliver(self, vaa: bytes, dest_chain_id: int) -> TransactionHash:
        """Sends transaction to the destination blockchain."""

        chain_lookup: Mapping[str, str] = json.loads(
            base64.b64decode(settings.chain_lookup).decode("utf-8")
        )

        web3_client = Web3(Web3.HTTPProvider(chain_lookup[str(dest_chain_id)]["rpc"]))

        contract = web3_client.eth.contract(
            address=chain_lookup[str(dest_chain_id)]["bridge_contract"], abi=self.abi
        )

        try:
            signed_transaction = await self.__craft_transaction(
                vaa=vaa, contract=contract, web3_client=web3_client
            )

            return web3_client.eth.send_raw_transaction(
                transaction=signed_transaction.rawTransaction
            )
        except Exception as e:
            self.logger.error("[EvmClient]: VAA delivery failed. Error: %s", e)
            raise EvmClientError(detail=str(e)) from e

    async def __craft_transaction(
        self, vaa: bytes, contract: Contract, web3_client: Web3
    ) -> SignedTransaction:
        """Craft a raw transaction to be sent to the blockchain."""

        max_priority_fee = web3_client.eth.max_priority_fee
        gas_price_estimate = web3_client.eth.gas_price

        transaction = contract.functions.processMessage(vaa).buildTransaction(
            {
                "from": settings.relayer_address,
                "nonce": web3_client.eth.get_transaction_count(
                    settings.relayer_address
                ),
                "maxFeePerGas": gas_price_estimate + max_priority_fee,
                "maxPriorityFeePerGas": max_priority_fee,
            }
        )

        return web3_client.eth.account.sign_transaction(
            transaction_dict=transaction, private_key=settings.relayer_private_key
        )
