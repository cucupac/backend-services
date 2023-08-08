from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field

from app.usecases.schemas.bridge import Bridges
from app.usecases.schemas.evm_transaction import EvmTransactionStatus


class Status(str, Enum):
    SUCCESS = "success"
    PENDING = "pending"
    FAILED = "failed"


class CrossChainTransaction(BaseModel):
    bridge: Bridges = Field(
        ...,
        description="The Ax-protocol-assigned bridge for the utilized bridge.",
        example=Bridges.WORMHOLE,
    )
    from_address: Optional[str] = Field(
        None,
        description="The transaction's sender address.",
        example="0x0CeC041cDB3AAB968C1a273bfC330aa410b5E2DF",
    )
    to_address: Optional[str] = Field(
        None,
        description="The transaction's recipient address.",
        example="0x0CeC041cDB3AAB968C1a273bfC330aa410b5E2DF",
    )
    source_chain_id: int = Field(
        ...,
        description="The source chain's bridging-protocol-assigned chain ID.",
        example=5,
    )
    dest_chain_id: int = Field(
        ...,
        description="The destination chain's bridging-protocol-assigned chain ID.",
        example=2,
    )
    amount: int = Field(
        ...,
        description="The amount of USX transferred.",
        example=1e18,
    )
    source_chain_tx_id: Optional[int] = Field(
        None,
        description="A foreign key to the chain transaction's table, denoting the source blockchain's transaction.",
        example=5,
    )
    dest_chain_tx_id: Optional[int] = Field(
        None,
        description="A foreign key to the chain transaction's table, denoting the destination blockchain's transaction.",
        example=2,
    )


class CrossChainTransactionInDB(CrossChainTransaction):
    """Database Object."""

    id: int = Field(
        ...,
        description="The unique identifier and primary key for the transactions table.",
        example=1,
    )
    created_at: datetime = Field(
        ...,
        description="The time that the transaction object was created.",
        example="2020-02-11 17:47:44.170522",
    )
    updated_at: datetime = Field(
        ...,
        description="The time that the transaction object was updated.",
        example="2020-02-11 17:47:44.170522",
    )


class CrossChainTxJoinEvmTx(CrossChainTransactionInDB):
    source_chain_tx_status: EvmTransactionStatus = Field(
        ...,
        description="The status of the source-chain evm transaciton.",
        example=EvmTransactionStatus.SUCCESS,
    )
    dest_chain_tx_status: EvmTransactionStatus = Field(
        ...,
        description="The status of the destination-chain evm transaciton.",
        example=EvmTransactionStatus.SUCCESS,
    )


class UpdateCrossChainTransaction(BaseModel):
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    source_chain_tx_id: Optional[int] = None
    dest_chain_tx_id: Optional[int] = None


class TransactionResponse(CrossChainTransaction):
    """
    The reponse model returned, via API endpoint, when a user queries for
    transaction by source chain ID and transaction hash.
    """

    status: Status = Field(
        ...,
        description="The status of the cross-chain USX transaction.",
        example=Status.SUCCESS,
    )
