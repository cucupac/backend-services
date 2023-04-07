from typing import Any, List, Mapping

from eth_account.datastructures import SignedTransaction
from web3 import Web3
from web3.contract import Contract

from app.dependencies import BRIDGE_DATA
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
        self,
        remote_data: MinimumFees,
        contract: Contract,
        web3_client: Web3,
        post_london_upgrade: bool,
    ) -> SignedTransaction:
        """Craft a raw transaction to be sent to the blockchain."""

        transaction_builder = {
            "from": settings.wh_bridge_admin_address,
            "nonce": web3_client.eth.get_transaction_count(
                settings.wh_bridge_admin_address
            ),
        }

        gas_price_estimate = web3_client.eth.gas_price

        if post_london_upgrade:
            max_priority_fee = web3_client.eth.max_priority_fee
            transaction_builder["maxFeePerGas"] = gas_price_estimate + max_priority_fee
            transaction_builder["maxPriorityFeePerGas"] = max_priority_fee
        else:
            transaction_builder["gasPrice"] = gas_price_estimate

        wormhole_chain_ids = await self.__translate_bridge_ids(
            chain_ids=remote_data.remote_chain_ids
        )

        transaction = contract.functions.setSendFees(
            wormhole_chain_ids, remote_data.remote_fees
        ).buildTransaction(transaction_builder)

        return web3_client.eth.account.sign_transaction(
            transaction_dict=transaction,
            private_key=settings.wh_bridge_admin_private_key,
        )

    async def estimate_gas_units(
        self, contract: Contract, web3_client: Web3, post_london_upgrade: bool
    ) -> int:
        """Estimates a transaction's gas information."""

        transaction_builder = {
            "from": settings.wh_bridge_admin_address,
            "nonce": web3_client.eth.get_transaction_count(
                settings.wh_bridge_admin_address
            ),
        }

        gas_price_estimate = web3_client.eth.gas_price

        if post_london_upgrade:
            max_priority_fee = web3_client.eth.max_priority_fee
            transaction_builder["maxFeePerGas"] = gas_price_estimate + max_priority_fee
            transaction_builder["maxPriorityFeePerGas"] = max_priority_fee
        else:
            transaction_builder["gasPrice"] = gas_price_estimate

        wormhole_chain_ids = await self.__translate_bridge_ids(
            chain_ids=self.mock_set_send_fees_params.remote_chain_ids,
        )

        transaction = contract.functions.setSendFees(
            wormhole_chain_ids,
            self.mock_set_send_fees_params.remote_fees,
        ).buildTransaction(transaction_builder)

        # TODO: Esnsure gas estimation is accurate, and add a margin
        return web3_client.eth.estimate_gas(transaction)

    async def __translate_bridge_ids(self, chain_ids: List[int]) -> List[int]:
        """Translates actual chain IDs to Wormhole chain IDs."""

        return [
            BRIDGE_DATA[actual_chain_id]["wormhole"]["chain_id"]
            for actual_chain_id in chain_ids
        ]
