from enum import Enum
from typing import Optional

from hexbytes import HexBytes
from pydantic import BaseModel, Field


class Ecosystem(str, Enum):
    EVM = "EVM"
    SOLANA = "SOLANA"
    APTOS = "APTOS"


class Chains(int, Enum):
    ETHEREUM = 1
    BSC = 56
    POLYGON = 137
    AVALANCHE = 43114
    FANTOM = 250
    ARBITRUM = 42161
    CELO = 42220
    OPTIMISM = 10


class BlockchainErrors(str, Enum):
    MESSAGE_PROCESSED = "Message already processed."
    TX_RECEIPT_STATUS_NOT_ONE = "Tx receipt exists, but status is not 1."
    TX_HASH_NOT_IN_CHAIN = "is not in the chain after"


class TransactionHash(HexBytes):
    """Blockchain transaction hash."""


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
