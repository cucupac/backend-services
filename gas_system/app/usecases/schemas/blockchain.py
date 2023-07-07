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


class TransactionHash(HexBytes):
    """Blockchain transaction hash."""


class BlockchainClientException(Exception):
    """Errors raised when interacting with Blockchain nodes."""

    detail: str


class BlockchainClientError(BlockchainClientException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.detail = kwargs.get("detail")


class ComputeCosts(BaseModel):
    median_gas_price: Optional[int] = Field(
        None,
        description="If post-london-upgrade, the sum of the median base fee per gas and the median priority fee over the last 100 blocks. If pre-london-upgrade, the median of gas price of the last 100 blocks.",
        example=24000000000,
    )
    gas_units: Optional[int] = Field(
        None,
        description="The estimated amount of gas units necessary to deliver a message to the destination chain.",
        example=255000,
    )
    native_value_usd: Optional[float] = Field(
        None,
        description="The value of the native currency in USD.",
        example=1850,
    )


class PostLondonComputeCosts(ComputeCosts):
    next_block_base_fee: Optional[int] = Field(
        None,
        description="The base fee per gas for the next, upcoming block.",
        example=25000000000,
    )
    median_priority_fee: Optional[int] = Field(
        None,
        description="The median priority fee per gas over the last 100 blocks.",
        example=25000000000,
    )
