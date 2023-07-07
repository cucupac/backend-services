from enum import Enum
from math import ceil
from statistics import median

from hexbytes import HexBytes

from app.dependencies import CHAIN_DATA
from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.schemas.blockchain import (
    BlockchainClientError,
    ComputeCosts,
    PostLondonComputeCosts,
    TransactionHash,
)
from app.usecases.schemas.fees import MinimumFees
from tests import constants as constant


class EvmResult(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class MockWormholeBridgeEvmClient(IBlockchainClient):
    def __init__(self, result: EvmResult, chain_id: int) -> None:
        self.result = result
        self.chain_id = chain_id
        self.post_london_strategy = (
            CHAIN_DATA[self.chain_id]["post_london_upgrade"]
            and CHAIN_DATA[self.chain_id]["has_fee_history"]
        )

    async def update_fees(
        self, remote_data: MinimumFees, compute_costs: ComputeCosts
    ) -> TransactionHash:
        """Sends transaction to the destination blockchain."""
        if self.result != EvmResult.FAILURE:
            return HexBytes(constant.TEST_TRANSACTION_HASH)
        raise BlockchainClientError(detail=constant.EVM_CLIENT_ERROR_DETAIL)

    async def estimate_fees(self) -> ComputeCosts:
        """Estimates a transaction's gas information."""

        if self.post_london_strategy:
            compute_costs = PostLondonComputeCosts(
                median_gas_price=ceil(median(constant.MOCK_GAS_PRICES)),
                next_block_base_fee=constant.MOCK_BASE_FEES_PER_GAS[-1],
                median_priority_fee=ceil(
                    median(constant.MOCK_MAX_PRIORITY_FEES_PER_GAS)
                ),
            )
        else:
            compute_costs = ComputeCosts(
                median_gas_price=constant.MOCK_GAS_PRICE,
            )
        compute_costs.gas_units = constant.MOCK_GAS_UNITS
        return compute_costs
