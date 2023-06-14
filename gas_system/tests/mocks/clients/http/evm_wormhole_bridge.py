from enum import Enum

from hexbytes import HexBytes

from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.schemas.blockchain import (
    BlockchainClientError,
    ComputeCosts,
    TransactionHash,
)
from app.usecases.schemas.fees import MinimumFees
from tests import constants as constant


class EvmResult(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class MockWormholeBridgeEvmClient(IBlockchainClient):
    def __init__(self, result: EvmResult) -> None:
        self.result = result

    async def update_fees(self, remote_data: MinimumFees) -> TransactionHash:
        """Sends transaction to the destination blockchain."""
        if self.result == EvmResult.SUCCESS:
            return HexBytes(constant.TEST_TRANSACTION_HASH)
        raise BlockchainClientError(detail=constant.EVM_CLIENT_ERROR_DETAIL)

    async def estimate_fees(self) -> ComputeCosts:
        """Estimates a transaction's gas information."""
        if self.result == EvmResult.SUCCESS:
            return ComputeCosts(
                gas_price=constant.MOCK_GAS_PRICE, gas_units=constant.MOCK_GAS_UNITS
            )
        raise BlockchainClientError(detail=constant.EVM_CLIENT_ERROR_DETAIL)
