from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AxChains(int, Enum):
    ETHEREUM = 1
    OPTIMISM = 2
    ARBITRUM = 3
    POLYGON = 4
    GNOSIS = 5
    CELO = 6
    FANTOM = 7
    AVALANCHE = 8
    BSC = 9


class BlockchainErrors(str, Enum):
    TX_RECEIPT_STATUS_NOT_ONE = "Tx receipt exists, but status is not 1."
    TX_HASH_NOT_IN_CHAIN = "is not in the chain after"


class BlockchainClientException(Exception):
    """Errors raised when interacting with Blockchain nodes."""

    detail: str


class BlockchainClientError(BlockchainClientException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.detail = kwargs.get("detail")


class TransactionReceipt(BaseModel):
    status: int


class TransactionReceiptResponse(BaseModel):
    receipt: Optional[TransactionReceipt] = Field(
        None,
        description="The extracted version of the transaction object received from the blockchain.",
        example=TransactionReceipt(status=1),
    )
    error: Optional[str] = Field(
        None,
        description="Error pertaining to relay.",
        example="An error happend, and here's why.",
    )
