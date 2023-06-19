from enum import Enum

from hexbytes import HexBytes

from app.dependencies import CHAIN_DATA
from app.settings import settings
from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.schemas.blockchain import (
    BlockchainClientError,
    Chains,
    ComputeCosts,
    TransactionHash,
)
from app.usecases.schemas.evm import GasPrices
from app.usecases.schemas.fees import MinimumFees
from tests import constants as constant


class EvmResult(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    MEDIAN_TESTING = "MEDIAN_TESTING"


class MockWormholeBridgeEvmClient(IBlockchainClient):
    def __init__(self, result: EvmResult, latest_blocks: int, chain_id: int) -> None:
        self.result = result
        self.latest_blocks = latest_blocks
        self.chain_id = chain_id

    async def update_fees(self, remote_data: MinimumFees) -> TransactionHash:
        """Sends transaction to the destination blockchain."""
        if self.result != EvmResult.FAILURE:
            return HexBytes(constant.TEST_TRANSACTION_HASH)
        raise BlockchainClientError(detail=constant.EVM_CLIENT_ERROR_DETAIL)

    async def estimate_fees(self) -> ComputeCosts:
        """Estimates a transaction's gas information."""

        if (
            self.result == EvmResult.MEDIAN_TESTING
            and self.chain_id == constant.TEST_TOO_EXPENSIVE_CHAIN
        ):
            gas_price = (
                constant.MOCK_BASE_FEES_PER_GAS[-1]
                + constant.MOCK_MAX_PRIORITY_FEES_PER_GAS[-1]
            ) * settings.max_acceptable_fee_multiplier
            return ComputeCosts(
                gas_price=gas_price,
                gas_units=constant.MOCK_GAS_UNITS,
            )
        if CHAIN_DATA[self.chain_id]["post_london_upgrade"]:
            return ComputeCosts(
                gas_price=constant.MOCK_BASE_FEES_PER_GAS[-1]
                + constant.MOCK_MAX_PRIORITY_FEES_PER_GAS[-1],
                gas_units=constant.MOCK_GAS_UNITS,
            )
        return ComputeCosts(
            gas_price=constant.MOCK_GAS_PRICES[-1],
            gas_units=constant.MOCK_GAS_UNITS,
        )

    async def get_gas_prices(self, block_count: int) -> GasPrices:
        """Returns gas prices over specified number of recent blocks."""

        if self.result == EvmResult.MEDIAN_TESTING:
            if self.chain_id == Chains.ETHEREUM:
                new_high_base_fee = (
                    constant.MOCK_BASE_FEES_PER_GAS[-1]
                    * settings.max_acceptable_fee_multiplier
                )
                return GasPrices(
                    base_fee_per_gas_list=constant.MOCK_BASE_FEES_PER_GAS
                    + [new_high_base_fee],
                    max_priority_fee_per_gas_list=constant.MOCK_MAX_PRIORITY_FEES_PER_GAS,
                )
            if CHAIN_DATA[self.chain_id]["post_london_upgrade"]:
                return GasPrices(
                    base_fee_per_gas_list=constant.MOCK_BASE_FEES_PER_GAS,
                    max_priority_fee_per_gas_list=constant.MOCK_MAX_PRIORITY_FEES_PER_GAS[
                        :-1
                    ],
                )
            return GasPrices(gas_price_list=constant.MOCK_GAS_PRICES)

        if CHAIN_DATA[self.chain_id]["post_london_upgrade"]:
            return GasPrices(
                base_fee_per_gas_list=constant.MOCK_BASE_FEES_PER_GAS,
                max_priority_fee_per_gas_list=constant.MOCK_MAX_PRIORITY_FEES_PER_GAS[
                    :-1
                ],
            )
        return GasPrices(gas_price_list=constant.MOCK_GAS_PRICES)
