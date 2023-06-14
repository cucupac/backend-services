from typing import Any, List, Mapping
from logging import Logger

from eth_account.datastructures import SignedTransaction
from web3 import AsyncHTTPProvider, AsyncWeb3

from app.dependencies import BRIDGE_DATA, CHAIN_DATA
from app.settings import settings
from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.schemas.fees import MinimumFees
from app.usecases.schemas.blockchain import (
    BlockchainClientError,
    ComputeCosts,
    TransactionHash,
)


class WormholeBridgeEvmClient(IBlockchainClient):
    def __init__(
        self,
        abi: List[Mapping[str, Any]],
        chain_id: int,
        rpc_url: str,
        mock_set_send_fees_params: MinimumFees,
        logger: Logger,
    ) -> None:
        self.abi = abi
        self.chain_id = chain_id
        self.rpc_url = rpc_url
        self.mock_set_send_fees_params = mock_set_send_fees_params
        self.web3_client = AsyncWeb3(AsyncHTTPProvider(self.rpc_url))
        self.contract = self.web3_client.eth.contract(
            address=self.web3_client.to_checksum_address(settings.evm_wormhole_bridge),
            abi=abi,
        )
        self.logger = logger

    async def update_fees(self, remote_data: MinimumFees) -> TransactionHash:
        """Sends transaction to the blockchain."""

        try:
            signed_transaction = await self.__get_signed_transaction(
                remote_data=remote_data,
            )

            return await self.web3_client.eth.send_raw_transaction(
                transaction=signed_transaction.rawTransaction
            )
        except Exception as e:
            self.logger.error("[EvmClient]: Fee update failed: %s", e)
            raise BlockchainClientError(detail=str(e)) from e

    async def estimate_fees(self) -> ComputeCosts:
        """Estimates a transaction's gas information."""

        transaction_dict = await self.__construct_transaction()

        if transaction_dict.get("maxFeePerGas"):
            max_gas_price = transaction_dict["maxFeePerGas"]
        else:
            max_gas_price = transaction_dict["gasPrice"]

        wormhole_chain_ids = await self.__translate_bridge_ids(
            chain_ids=self.mock_set_send_fees_params.remote_chain_ids
        )

        transaction = await self.contract.functions.setSendFees(
            wormhole_chain_ids, self.mock_set_send_fees_params.remote_fees
        ).build_transaction(transaction_dict)

        estimated_gas_units = await self.web3_client.eth.estimate_gas(transaction)

        return ComputeCosts(
            gas_price=max_gas_price,
            gas_units=estimated_gas_units,
        )

    async def __get_signed_transaction(
        self,
        remote_data: MinimumFees,
    ) -> SignedTransaction:
        """Craft a raw transaction to be sent to the blockchain."""

        transaction_dict = await self.__construct_transaction()

        wormhole_chain_ids = await self.__translate_bridge_ids(
            chain_ids=remote_data.remote_chain_ids
        )

        transaction = await self.contract.functions.setSendFees(
            wormhole_chain_ids, remote_data.remote_fees
        ).build_transaction(transaction_dict)

        return self.web3_client.eth.account.sign_transaction(
            transaction_dict=transaction, private_key=settings.fee_setter_private_key
        )

    async def __construct_transaction(self) -> Mapping[str, Any]:
        """Constructs transaction dictionary."""

        # Obtain destination chain information
        post_london_upgrade = CHAIN_DATA[self.chain_id]["post_london_upgrade"]
        has_fee_history = CHAIN_DATA[self.chain_id]["has_fee_history"]

        # Build transaction
        transaction_dict = {
            "from": self.web3_client.to_checksum_address(settings.fee_setter_address),
            "nonce": await self.web3_client.eth.get_transaction_count(
                settings.fee_setter_address
            ),
        }

        if post_london_upgrade:
            if has_fee_history:
                fee_history = await self.web3_client.eth.fee_history(
                    block_count=1,
                    newest_block="latest",
                    reward_percentiles=[settings.priority_fee_percentile],
                )

                base_fee_per_gas = fee_history.baseFeePerGas[-1]
                max_priority_fee = fee_history.reward[0][0]
            else:
                base_fee_per_gas = await self.web3_client.eth.gas_price
                max_priority_fee = await self.web3_client.eth.max_priority_fee

            transaction_dict["maxFeePerGas"] = base_fee_per_gas + max_priority_fee
            transaction_dict["maxPriorityFeePerGas"] = max_priority_fee
        else:
            transaction_dict["gasPrice"] = await self.web3_client.eth.gas_price

        return transaction_dict

    async def __translate_bridge_ids(self, chain_ids: List[int]) -> List[int]:
        """Translates actual chain IDs to Wormhole chain IDs."""

        return [
            BRIDGE_DATA[actual_chain_id]["wormhole"]["chain_id"]
            for actual_chain_id in chain_ids
        ]
