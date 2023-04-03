from typing import Any, List, Mapping

from eth_account.datastructures import SignedTransaction
from web3 import Web3
from web3.contract import Contract

from app.settings import settings
from app.usecases.interfaces.clients.http.bridge import IBridgeClient


class WormholeBridgeClient(IBridgeClient):
    def __init__(
        self,
        address: str,
        abi: List[Mapping[str, Any]],
    ) -> None:
        self.abi = abi
        self.address = address

    async def craft_transaction(
        self, payload: bytes, contract: Contract, web3_client: Web3
    ) -> SignedTransaction:
        """Craft a raw transaction to be sent to the blockchain."""

        max_priority_fee = web3_client.eth.max_priority_fee
        gas_price_estimate = web3_client.eth.gas_price

        transaction = contract.functions.processMessage(payload).buildTransaction(
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
