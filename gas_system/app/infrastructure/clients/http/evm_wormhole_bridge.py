# pylint: disable=too-many-instance-attributes, too-many-arguments
from logging import Logger
from math import ceil
from statistics import median
from typing import Any, List, Mapping, Union

from eth_account.datastructures import SignedTransaction
from web3 import AsyncHTTPProvider, AsyncWeb3
from web3.middleware import async_geth_poa_middleware

from app.dependencies import BRIDGE_DATA, CHAIN_DATA
from app.settings import settings
from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.schemas.blockchain import (
    BlockchainClientError,
    ComputeCosts,
    PostLondonComputeCosts,
    TransactionHash,
)
from app.usecases.schemas.evm import PostLondonGasPrices, PreLondonGasPrices
from app.usecases.schemas.fees import MinimumFees


class WormholeBridgeEvmClient(IBlockchainClient):
    def __init__(
        self,
        abi: List[Mapping[str, Any]],
        chain_id: int,
        rpc_url: str,
        mock_payload: bytes,
        logger: Logger,
    ) -> None:
        self.abi = abi
        self.chain_id = chain_id
        self.rpc_url = rpc_url
        self.payload = mock_payload
        self.web3_client = AsyncWeb3(AsyncHTTPProvider(self.rpc_url))
        self.contract = self.web3_client.eth.contract(
            address=self.web3_client.to_checksum_address(settings.evm_wormhole_bridge),
            abi=abi,
        )
        self.web3_client.middleware_onion.inject(async_geth_poa_middleware, layer=0)
        self.post_london_strategy = (
            CHAIN_DATA[self.chain_id]["post_london_upgrade"]
            and CHAIN_DATA[self.chain_id]["has_fee_history"]
        )
        self.logger = logger

    async def update_fees(
        self, remote_data: MinimumFees, compute_costs: ComputeCosts
    ) -> TransactionHash:
        """Sends transaction to the blockchain."""

        transaction_dict = await self.__construct_update_transaction(
            compute_costs=compute_costs
        )

        try:
            signed_transaction = await self.__get_signed_transaction(
                remote_data=remote_data, transaction_dict=transaction_dict
            )

            return await self.web3_client.eth.send_raw_transaction(
                transaction=signed_transaction.rawTransaction
            )
        except Exception as e:
            self.logger.error(
                "[WormholeBridgeEvmClient]: Chain ID: %s; fee update failed: %s",
                self.chain_id,
                e,
            )
            raise BlockchainClientError(detail=str(e)) from e

    async def estimate_fees(self) -> ComputeCosts:
        """Estimates a transaction's gas information."""

        gas_info = await self.__get_gas_prices()

        transaction_dict = await self.__construct_estimation_transaction(
            gas_info=gas_info
        )

        if isinstance(gas_info, PostLondonGasPrices):
            compute_costs = PostLondonComputeCosts(
                median_gas_price=transaction_dict["maxFeePerGas"],
                next_block_base_fee=gas_info.base_fee_per_gas_list[-1],
                median_priority_fee=ceil(
                    median(gas_info.max_priority_fee_per_gas_list)
                ),
            )
        else:
            compute_costs = ComputeCosts(
                median_gas_price=transaction_dict["gasPrice"],
            )

        transaction = await self.contract.functions.processMessage(
            self.payload
        ).build_transaction(transaction_dict)

        compute_costs.gas_units = await self.web3_client.eth.estimate_gas(transaction)

        return compute_costs

    async def __get_gas_prices(self) -> Union[PostLondonGasPrices, PreLondonGasPrices]:
        """Returns gas prices for recent blocks."""

        if self.post_london_strategy:
            fee_history = await self.web3_client.eth.fee_history(
                block_count=settings.recent_blocks,
                newest_block="latest",
                reward_percentiles=[settings.priority_fee_percentile],
            )

            base_fee_per_gas_list = fee_history.baseFeePerGas
            max_priority_fee_list = [
                percentile_list[0] for percentile_list in fee_history.reward
            ]

            return PostLondonGasPrices(
                base_fee_per_gas_list=base_fee_per_gas_list,
                max_priority_fee_per_gas_list=max_priority_fee_list,
            )
        return PreLondonGasPrices(median_gas_price=await self.web3_client.eth.gas_price)

    async def __construct_update_transaction(
        self, compute_costs: ComputeCosts
    ) -> Mapping[str, Any]:
        """
        Description: constructs transcation for fee updates.
        Gas strategy:
            Post EIP-1559: next block base fee, median priority fee over the last 100 blocks.
                - Multi-block median priority fee protects against black swan priority fees.
                - Non-discriminitory toward base fees.
            Pre EIP-1559: 50th percentile gas price over the last 100 blocks.
                - Multi-block median protects against black swan gas prices.
        """

        transaction_dict = {
            "from": self.web3_client.to_checksum_address(settings.fee_setter_address),
            "nonce": await self.web3_client.eth.get_transaction_count(
                settings.fee_setter_address
            ),
        }

        if isinstance(compute_costs, PostLondonComputeCosts):
            base_fee_per_gas = compute_costs.next_block_base_fee
            priority_fee_per_gas = compute_costs.median_priority_fee
            max_fee_per_gas = base_fee_per_gas + priority_fee_per_gas

            transaction_dict["maxFeePerGas"] = max_fee_per_gas
            transaction_dict["maxPriorityFeePerGas"] = priority_fee_per_gas
        else:
            transaction_dict["gasPrice"] = compute_costs.median_gas_price

        return transaction_dict

    async def __construct_estimation_transaction(
        self, gas_info: Union[PostLondonGasPrices, PreLondonGasPrices] = None
    ) -> Mapping[str, Any]:
        """
        Description: constructs transaction for remote fee estimation.
        Gas strategy:
            Post EIP-1559: median base fee, median priority fee over the last 100 blocks.
                - Multi-block median protects against black swan gas prices.
            Pre EIP-1559: 50th percentile gas price over the last 100 blocks.
                - Multi-block median protects against black swan gas prices.
        """

        transaction_dict = {
            "from": self.web3_client.to_checksum_address(settings.relayer_address),
            "nonce": await self.web3_client.eth.get_transaction_count(
                settings.relayer_address
            ),
        }

        if isinstance(gas_info, PostLondonGasPrices):
            base_fee_per_gas = ceil(median(gas_info.base_fee_per_gas_list))
            priority_fee_per_gas = ceil(median(gas_info.max_priority_fee_per_gas_list))
            max_fee_per_gas = base_fee_per_gas + priority_fee_per_gas

            transaction_dict["maxFeePerGas"] = max_fee_per_gas
            transaction_dict["maxPriorityFeePerGas"] = priority_fee_per_gas
        else:
            transaction_dict["gasPrice"] = gas_info.median_gas_price

        return transaction_dict

    async def __get_signed_transaction(
        self, remote_data: MinimumFees, transaction_dict: Mapping[str, Any]
    ) -> SignedTransaction:
        """Craft a raw transaction to be sent to the blockchain."""

        wormhole_chain_ids = await self.__translate_bridge_ids(
            chain_ids=remote_data.remote_chain_ids
        )

        transaction = await self.contract.functions.setSendFees(
            wormhole_chain_ids, remote_data.remote_fees
        ).build_transaction(transaction_dict)

        return self.web3_client.eth.account.sign_transaction(
            transaction_dict=transaction, private_key=settings.fee_setter_private_key
        )

    async def __translate_bridge_ids(self, chain_ids: List[int]) -> List[int]:
        """Translates actual chain IDs to Wormhole chain IDs."""

        return [
            BRIDGE_DATA[actual_chain_id]["wormhole"]["chain_id"]
            for actual_chain_id in chain_ids
        ]
