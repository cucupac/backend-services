from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.usecases.schemas.bridge import Bridges


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


class UpdateCrossChainTransaction(BaseModel):
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    source_chain_tx_id: Optional[int] = None
    dest_chain_tx_id: Optional[int] = None


# TODO: come back to this...
# class TransactionResponse(BaseModel):
#     """
#     The reponse model returned, via API endpoint, when a user queries for
#     transaction by source chain ID and transaction hash.
#     """

#     source_chain_id: str = Field(
#         ...,
#         description="The source chain's bridge-protocol-assigned chain ID.",
#         example=5,
#     )
#     dest_chain_id: int = Field(
#         ...,
#         description="The destination chain's bridging-protocol-assigned chain ID.",
#         example=2,
#     )
#     transaction_hash: str = Field(
#         ...,
#         description="The hash of the submitted, source-chain transaction.",
#         example="0xb5c8bd9430b6cc87a0e2fe110ece6bf527fa4f170a4bc8cd032f768fc5219838",
#     )
#     status: Status = Field(
#         ...,
#         description="The status of the cross-chain transaction.",
#         example="success",
#     )
#     created_at: datetime = Field(
#         ...,
#         description="The time that the transaction object was created.",
#         example="2020-02-11 17:47:44.170522",
#     )
#     updated_at: datetime = Field(
#         ...,
#         description="The time that the transaction object was updated.",
#         example="2020-02-11 17:47:44.170522",
#     )
