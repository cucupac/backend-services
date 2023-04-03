from typing import Any, List, Mapping

from eth_account.datastructures import SignedTransaction
from web3 import Web3
from web3.contract import Contract

from app.settings import settings
from app.usecases.interfaces.clients.http.bridge import IBridgeClient
from app.usecases.schemas.fees import MinimumFees


class WormholeBridgeClient(IBridgeClient):
    def __init__(
        self,
        address: str,
        abi: List[Mapping[str, Any]],
        mock_set_send_fees_params: MinimumFees,
    ) -> None:
        self.abi = abi
        self.mock_set_send_fees_params = mock_set_send_fees_params
        self.address = address

    async def craft_transaction(
        self, remote_data: MinimumFees, contract: Contract, web3_client: Web3
    ) -> SignedTransaction:
        """Craft a raw transaction to be sent to the blockchain."""

        max_priority_fee = web3_client.eth.max_priority_fee
        gas_price_estimate = web3_client.eth.gas_price

        transaction = contract.functions.setSendFees(
            remote_data.remote_chain_ids, remote_data.remote_fees
        ).buildTransaction(
            {
                "from": settings.wh_bridge_admin_address,
                "nonce": web3_client.eth.get_transaction_count(
                    settings.wh_bridge_admin_address
                ),
                "maxFeePerGas": gas_price_estimate + max_priority_fee,
                "maxPriorityFeePerGas": max_priority_fee,
            }
        )

        return web3_client.eth.account.sign_transaction(
            transaction_dict=transaction,
            private_key=settings.wh_bridge_admin_private_key,
        )

    async def estimate_gas_units(self, contract: Contract, web3_client: Web3) -> int:
        """Estimates a transaction's gas information."""

        transaction = contract.functions.setSendFees(
            self.mock_set_send_fees_params.remote_chain_ids,
            self.mock_set_send_fees_params.remote_fees,
        ).buildTransaction(
            {
                "from": settings.wh_bridge_admin_address,
                "nonce": web3_client.eth.get_transaction_count(
                    settings.wh_bridge_admin_address
                ),
            }
        )

        # TODO: Esnsure gas estimation is accurate.
        return web3_client.eth.estimate_gas(transaction)
