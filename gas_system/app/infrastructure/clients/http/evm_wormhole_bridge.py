# pylint: disable=too-many-instance-attributes, too-many-arguments
from logging import Logger
from typing import Any, List, Mapping
from statistics import median

from eth_account.datastructures import SignedTransaction
from web3 import AsyncHTTPProvider, AsyncWeb3
from web3.middleware import async_geth_poa_middleware

from app.dependencies import BRIDGE_DATA, CHAIN_DATA
from app.settings import settings
from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.schemas.blockchain import (
    BlockchainClientError,
    ComputeCosts,
    TransactionHash,
)
from app.usecases.schemas.evm import GasPrices
from app.usecases.schemas.fees import MinimumFees


class WormholeBridgeEvmClient(IBlockchainClient):
    def __init__(
        self,
        abi: List[Mapping[str, Any]],
        chain_id: int,
        latest_blocks: int,
        rpc_url: str,
        mock_payload: bytes,
        logger: Logger,
    ) -> None:
        self.abi = abi
        self.chain_id = chain_id
        self.latest_blocks = latest_blocks
        self.rpc_url = rpc_url
        self.payload = mock_payload
        self.web3_client = AsyncWeb3(AsyncHTTPProvider(self.rpc_url))
        self.contract = self.web3_client.eth.contract(
            address=self.web3_client.to_checksum_address(settings.evm_wormhole_bridge),
            abi=abi,
        )
        self.logger = logger
        self.web3_client.middleware_onion.inject(async_geth_poa_middleware, layer=0)

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
            self.logger.error(
                "[WormholeBridgeEvmClient]: Chain ID: %s; fee update failed: %s",
                self.chain_id,
                e,
            )
            raise BlockchainClientError(detail=str(e)) from e

    async def estimate_fees(
        self,
    ) -> ComputeCosts:
        """Estimates a transaction's gas information."""

        transaction_dict = await self.__construct_transaction(
            sender=settings.relayer_address
        )

        if transaction_dict.get("maxFeePerGas"):
            max_gas_price = transaction_dict["maxFeePerGas"]
        else:
            max_gas_price = transaction_dict["gasPrice"]

        transaction = await self.contract.functions.processMessage(
            self.payload
        ).build_transaction(transaction_dict)

        try:
            estimated_gas_units = await self.web3_client.eth.estimate_gas(transaction)
        except Exception as e:
            self.logger.error(
                "[WormholeBridgeEvmClient]: Chain ID: %s, fee estimation failed: %s",
                self.chain_id,
                e,
            )

        return ComputeCosts(
            gas_price=max_gas_price,
            gas_units=estimated_gas_units,
        )

    async def __get_signed_transaction(
        self,
        remote_data: MinimumFees,
    ) -> SignedTransaction:
        """Craft a raw transaction to be sent to the blockchain."""

        transaction_dict = await self.__construct_transaction(
            sender=settings.fee_setter_address
        )

        wormhole_chain_ids = await self.__translate_bridge_ids(
            chain_ids=remote_data.remote_chain_ids
        )

        transaction = await self.contract.functions.setSendFees(
            wormhole_chain_ids, remote_data.remote_fees
        ).build_transaction(transaction_dict)

        return self.web3_client.eth.account.sign_transaction(
            transaction_dict=transaction, private_key=settings.fee_setter_private_key
        )

    async def __construct_transaction(self, sender: str) -> Mapping[str, Any]:
        """Constructs transaction dictionary."""

        transaction_dict = {
            "from": self.web3_client.to_checksum_address(sender),
            "nonce": await self.web3_client.eth.get_transaction_count(sender),
        }

        if (
            CHAIN_DATA[self.chain_id]["post_london_upgrade"]
            and CHAIN_DATA[self.chain_id]["has_fee_history"]
        ):
            gas_prices = await self.get_gas_prices(block_count=1)
            transaction_dict["maxFeePerGas"] = (
                gas_prices.base_fee_per_gas_list[-1]
                + gas_prices.max_priority_fee_per_gas_list[-1]
            )
            transaction_dict[
                "maxPriorityFeePerGas"
            ] = gas_prices.max_priority_fee_per_gas_list[-1]
        else:
            transaction_dict["gasPrice"] = await self.web3_client.eth.gas_price

        return transaction_dict

    async def __translate_bridge_ids(self, chain_ids: List[int]) -> List[int]:
        """Translates actual chain IDs to Wormhole chain IDs."""

        return [
            BRIDGE_DATA[actual_chain_id]["wormhole"]["chain_id"]
            for actual_chain_id in chain_ids
        ]

    async def get_gas_prices(self, block_count: int) -> GasPrices:
        """Returns gas prices over specified number of recent blocks."""

        post_london_upgrade = CHAIN_DATA[self.chain_id]["post_london_upgrade"]
        has_fee_history = CHAIN_DATA[self.chain_id]["has_fee_history"]

        if post_london_upgrade and has_fee_history:
            fee_history = await self.web3_client.eth.fee_history(
                block_count=block_count,
                newest_block="latest",
                reward_percentiles=[settings.priority_fee_percentile],
            )

            base_fee_per_gas_list = fee_history.baseFeePerGas
            max_priority_fee_list = [
                percentile_list[0] for percentile_list in fee_history.reward
            ]

            return GasPrices(
                base_fee_per_gas_list=base_fee_per_gas_list,
                max_priority_fee_per_gas_list=max_priority_fee_list,
            )

        median_gas_prices_per_block = await self.__get_median_gas_prices(
            block_count=block_count
        )
        return GasPrices(gas_price_list=median_gas_prices_per_block)

    async def __get_median_gas_prices(self, block_count: int) -> List[int]:
        """Returns a list of median gas prices per block in the case of no available fee history."""

        latest_block_number = await self.web3_client.eth.block_number

        median_gas_prices_per_block = []
        for block_number in range(
            latest_block_number - block_count + 1, latest_block_number + 1
        ):
            block = await self.web3_client.eth.get_block(block_number, True)
            block_gas_prices = [tx["gasPrice"] for tx in block.transactions]
            median_gas_prices_per_block.append(median(block_gas_prices))

        return median_gas_prices_per_block
