from enum import Enum
from typing import Union, List

from web3.datastructures import AttributeDict

from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.schemas.events import SendToChain, ReceiveFromChain
import tests.constants as constant
from app.settings import settings


class EvmResult(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class MockEvmClientInsertFlow(IEvmClient):
    def __init__(self, result: EvmResult, chain_id: int) -> None:
        self.result = result
        self.chain_id = chain_id

    async def fetch_receipt(self, transaction_hash: str) -> AttributeDict:
        """Fetches the transaction receipt for a given transaction hash."""
        return

    async def fetch_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[Union[SendToChain, ReceiveFromChain]]:
        """Fetches events emitted from given contract, for a given block range.

        This mock function mimics a cross-chain message from celo to polygon for both
        Layer Zero and Wormhole."""

        send_to_chain_event = SendToChain(
            emitter_address=contract,
            block_number=from_block,
            block_hash=constant.WH_SOURCE_BLOCK_HASH,
            transaction_hash=constant.WH_SOURCE_TX_HASH,
            source_chain_id=constant.WH_SOURCE_CHAIN_ID,
            dest_chain_id=constant.WH_DEST_CHAIN_ID,
            amount=constant.TEST_AMOUNT,
            message_id=constant.TEST_MESSAGE_ID,
            from_address=constant.TEST_FROM_ADDRESS,
        )

        receive_from_chain_event = ReceiveFromChain(
            emitter_address=contract,
            block_number=from_block,
            block_hash=constant.WH_DEST_BLOCK_HASH,
            transaction_hash=constant.WH_DEST_TX_HASH,
            source_chain_id=constant.WH_SOURCE_CHAIN_ID,
            dest_chain_id=constant.WH_DEST_CHAIN_ID,
            amount=constant.TEST_AMOUNT,
            message_id=constant.TEST_MESSAGE_ID,
            to_address=constant.TEST_TO_ADDRESS,
        )

        if self.chain_id == constant.TEST_SOURCE_CHAIN_ID:
            """Source chain."""
            if contract == settings.evm_wormhole_bridge:
                return [send_to_chain_event]
            elif contract == settings.evm_layerzero_bridge:
                send_to_chain_event.transaction_hash = constant.LZ_SOURCE_TX_HASH
                send_to_chain_event.source_chain_id = constant.LZ_SOURCE_CHAIN_ID
                send_to_chain_event.dest_chain_id = constant.LZ_DEST_CHAIN_ID
                return [send_to_chain_event]

        elif self.chain_id == constant.TEST_DEST_CHAIN_ID:
            """Destination chain."""
            if contract == settings.evm_wormhole_bridge:
                return [receive_from_chain_event]
            elif contract == settings.evm_layerzero_bridge:
                receive_from_chain_event.transaction_hash = constant.LZ_DEST_TX_HASH
                receive_from_chain_event.source_chain_id = constant.LZ_SOURCE_CHAIN_ID
                receive_from_chain_event.dest_chain_id = constant.LZ_DEST_CHAIN_ID
                return [receive_from_chain_event]
        else:
            return []

    async def fetch_latest_block_number(self) -> int:
        """Fetches the latest block number."""

        return constant.TEST_BLOCK_NUMBER


class MockEvmClientUpdateFlow(IEvmClient):
    def __init__(self, result: EvmResult, chain_id: int) -> None:
        self.result = result
        self.chain_id = chain_id

    async def fetch_receipt(self, transaction_hash: str) -> AttributeDict:
        """Fetches the transaction receipt for a given transaction hash."""
        return

    async def fetch_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[Union[SendToChain, ReceiveFromChain]]:
        """Fetches events emitted from given contract, for a given block range."""

        if self.chain_id == constant.TEST_DEST_CHAIN_ID:
            """Destination chain."""

            if contract == settings.evm_wormhole_bridge:
                receive_from_chain_event = ReceiveFromChain(
                    emitter_address=contract,
                    block_number=from_block,
                    block_hash=constant.WH_DEST_BLOCK_HASH,
                    transaction_hash=constant.WH_DEST_TX_HASH,
                    source_chain_id=constant.WH_SOURCE_CHAIN_ID,
                    dest_chain_id=constant.WH_DEST_CHAIN_ID,
                    amount=constant.TEST_AMOUNT,
                    message_id=constant.TEST_MESSAGE_ID,
                    to_address=constant.TEST_TO_ADDRESS,
                )
            else:
                receive_from_chain_event = ReceiveFromChain(
                    emitter_address=contract,
                    block_number=from_block,
                    block_hash=constant.LZ_DEST_BLOCK_HASH,
                    transaction_hash=constant.LZ_DEST_TX_HASH,
                    source_chain_id=constant.LZ_SOURCE_CHAIN_ID,
                    dest_chain_id=constant.LZ_DEST_CHAIN_ID,
                    amount=constant.TEST_AMOUNT,
                    message_id=constant.TEST_MESSAGE_ID,
                    to_address=constant.TEST_TO_ADDRESS,
                )
            return [receive_from_chain_event]
        else:
            return []

    async def fetch_latest_block_number(self) -> int:
        """Fetches the latest block number."""

        return constant.TEST_BLOCK_NUMBER

    # return AttributeDict(
    #     {
    #         "blockHash": HexBytes(
    #             "0xaa23de51708eea91dc9dd497c6e2f281df5652732e8fad7da85c5097984cbae8"
    #         ),
    #         "blockNumber": 17635957,
    #         "contractAddress": None,
    #         "cumulativeGasUsed": 12265446,
    #         "effectiveGasPrice": 37043254326,
    #         "from": "0x9919ec3ef3782382FE1487c4a36b72f02E03189B",
    #         "gasUsed": 60825,
    #         "logs": [
    #             AttributeDict(
    #                 {
    #                     "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    #                     "topics": [
    #                         HexBytes(
    #                             "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    #                         ),
    #                         HexBytes(
    #                             "0x0000000000000000000000009919ec3ef3782382fe1487c4a36b72f02e03189b"
    #                         ),
    #                         HexBytes(
    #                             "0x0000000000000000000000003414b7fbf959deba4456bfed6af5e2e8af19a8db"
    #                         ),
    #                     ],
    #                     "data": HexBytes(
    #                         "0x000000000000000000000000000000000000000000000000000000037e11d600"
    #                     ),
    #                     "blockNumber": 17635957,
    #                     "transactionHash": HexBytes(
    #                         "0xee6d83e952211d845f1cd09cc7764989085916d96d09d82ca417a7e56cc56bfd"
    #                     ),
    #                     "transactionIndex": 111,
    #                     "blockHash": HexBytes(
    #                         "0xaa23de51708eea91dc9dd497c6e2f281df5652732e8fad7da85c5097984cbae8"
    #                     ),
    #                     "logIndex": 266,
    #                     "removed": False,
    #                 }
    #             )
    #         ],
    #         "logsBloom": HexBytes(
    #             "0x00000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008000008000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000010000000000010000000000000000000000000000000000000010000000000000100000000000000000000200000000008000000000000004000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    #         ),
    #         "status": 1,
    #         "to": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    #         "transactionHash": HexBytes(
    #             "0xee6d83e952211d845f1cd09cc7764989085916d96d09d82ca417a7e56cc56bfd"
    #         ),
    #         "transactionIndex": 111,
    #         "type": 2,
    #     }
    # )
