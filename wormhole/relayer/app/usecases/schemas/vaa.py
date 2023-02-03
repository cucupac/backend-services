from typing import List

from pydantic import BaseModel, Field


class WormholeSignature(BaseModel):
    index: int
    signature: bytes


class ParsedPayload(BaseModel):
    from_address: str = Field(
        ...,
        description="The source-chain address, from which money was transferred.",
        example="0x0E31Cc997F3C3bBD3091449eF03DAB3b7455A02D",
    )
    to_address: str = Field(
        ...,
        description="The destination-chain address that will receive money.",
        example="0x0E31Cc997F3C3bBD3091449eF03DAB3b7455A02D",
    )
    dest_chain_id: int = Field(
        ...,
        description="The Wormhole-ascribed destination-chain ID.",
        example=2,
    )
    amount: int = Field(
        ...,
        description="That amount of money to be transferred (18 decimals).",
        example=1e18,
    )


class ParsedVaa(BaseModel):
    """Vaa object after parsing raw VAA bytes."""

    version: int = Field(
        ...,
        description="The Wormhole-ascribed version.",
        example=1,
    )
    guardian_set_index: int = Field(
        ...,
        description="Index of guardian set used.",
        example=3,
    )
    guardian_signatures: List[WormholeSignature] = Field(
        ...,
        description="A list of the 19 Wormhole signatures.",
        example=[
            {
                "index": 0,
                "signature": b"\x9dum\x00'\xdc\x80\xfb\x8e\x92\xa0\xacG\xe8\x18\xd5\x00\xccrr\x8c\x07\xedNL\nb/nT\x81\x92uL2W)U\xe0u!\x13W\x19:\xd2\x87\xbf\x0f\xf1\xb7\xf0\xc1\x9a\xae\x1cU\xef1\xb6\xbf+\x88\x16\x00",
            }
        ],
    )
    timestamp: int = Field(
        ...,
        description="The time that the VAA was verified at.",
        example=1674071813,
    )
    nonce: int = Field(
        ...,
        description="Nonce.",
        example=0,
    )
    emitter_chain: int = Field(
        ...,
        description="The Wormhole-ascribed source-chain ID.",
        example=5,
    )
    emitter_address: str = Field(
        ...,
        description="The address of the contract on the source-chain that emitted the cross-chain message.",
        example="0xbf8a1387d4682b5b431cea8f53edd5e7a7834861",
    )
    sequence: int = Field(
        ...,
        description="The emitter contract's chronological sequence of the cross-chain message.",
        example=35,
    )
    consistency_level: int = Field(
        ...,
        description="The level of finality to reach before emitting the Wormhole VAA.",
        example=200,
    )
    payload: ParsedPayload = Field(
        ...,
        description="The VAA's payload to be decoded on the destination chain.",
        example=None,
    )
    hash: bytes = Field(
        ...,
        description="The hash of the VAA.",
        example=b"L(:\xb7\x1d\xa4\xdb\x99\xb7\xfa\xee\xe2\xb9MUQ.\x97\xbd\xa2\xa6<\xee\xce\xe1\x88\xd3N\xd2\x0c\x7f\xf0",
    )
