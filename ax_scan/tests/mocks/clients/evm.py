from enum import Enum
from typing import List, Union

from web3.datastructures import AttributeDict

import tests.constants as constant
from app.dependencies import CHAIN_DATA
from app.settings import settings
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.schemas.blockchain import BlockchainClientError, TransactionReceipt
from app.usecases.schemas.events import Mint, ReceiveFromChain, SendToChain


class EvmResult(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class MockEvmClientTxReciept(IEvmClient):
    def __init__(
        self, result: EvmResult, status_is_one: bool, tx_exists: bool, chain_id: int
    ) -> None:
        self.result = result
        self.status_is_one = status_is_one
        self.tx_exists = tx_exists
        self.chain_id = chain_id

    async def fetch_receipt(self, transaction_hash: str) -> AttributeDict:
        """Fetches the transaction receipt for a given transaction hash."""
        if self.result == EvmResult.SUCCESS:
            if self.status_is_one:
                return TransactionReceipt(
                    status=1,
                    gas_used=constant.TEST_GAS_USED,
                    gas_price=constant.TEST_GAS_PRICE,
                )
            return TransactionReceipt(
                status=0,
                gas_used=constant.TEST_GAS_USED,
                gas_price=constant.TEST_GAS_PRICE,
            )
        if not self.tx_exists:
            raise BlockchainClientError(detail=constant.NOT_FOUND_ERROR)
        raise BlockchainClientError(detail="Some general error.")

    async def fetch_transfer_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[Union[SendToChain, ReceiveFromChain]]:
        return []

    async def fetch_mint_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[Mint]:
        """Fetches mint events emitted from given contract, for a given block range."""
        return []

    async def fetch_latest_block_number(self) -> int:
        """Fetches the latest block number."""

        return constant.TEST_BLOCK_NUMBER


class MockEvmClientInsertFlow(IEvmClient):
    def __init__(self, result: EvmResult, chain_id: int) -> None:
        self.result = result
        self.chain_id = chain_id

    async def fetch_receipt(self, transaction_hash: str) -> AttributeDict:
        """Fetches the transaction receipt for a given transaction hash."""
        return

    async def fetch_transfer_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[Union[SendToChain, ReceiveFromChain]]:
        """Fetches cross-chain transfer events emitted from given contract, for a given block range.

        This mock function mimics a cross-chain message from celo to polygon for both
        Layer Zero and Wormhole."""

        send_to_chain_event = SendToChain(
            emitter_address=contract,
            block_number=from_block,
            block_hash=constant.WH_SRC_BLOCK_HASH,
            transaction_hash=constant.WH_SRC_TX_HASH,
            source_chain_id=constant.WH_SRC_CHAIN_ID,
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
            source_chain_id=constant.WH_SRC_CHAIN_ID,
            dest_chain_id=constant.WH_DEST_CHAIN_ID,
            amount=constant.TEST_AMOUNT,
            message_id=constant.TEST_MESSAGE_ID,
            to_address=constant.TEST_TO_ADDRESS,
        )

        if self.chain_id == constant.TEST_SRC_CHAIN_ID:
            if contract == settings.evm_wormhole_bridge:
                return [send_to_chain_event]
            send_to_chain_event.transaction_hash = constant.LZ_SRC_TX_HASH
            send_to_chain_event.source_chain_id = constant.LZ_SRC_CHAIN_ID
            send_to_chain_event.dest_chain_id = constant.LZ_DEST_CHAIN_ID
            return [send_to_chain_event]

        if self.chain_id == constant.TEST_DEST_CHAIN_ID:
            if contract == settings.evm_wormhole_bridge:
                return [receive_from_chain_event]
            receive_from_chain_event.transaction_hash = constant.LZ_DEST_TX_HASH
            receive_from_chain_event.source_chain_id = constant.LZ_SRC_CHAIN_ID
            receive_from_chain_event.dest_chain_id = constant.LZ_DEST_CHAIN_ID
            return [receive_from_chain_event]
        return []

    async def fetch_mint_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[Mint]:
        """Fetches mint events emitted from given contract, for a given block range."""
        return []

    async def fetch_latest_block_number(self) -> int:
        """Fetches the latest block number."""

        return constant.TEST_BLOCK_NUMBER


class MockEvmClientDestOnly(IEvmClient):
    def __init__(self, result: EvmResult, chain_id: int) -> None:
        self.result = result
        self.chain_id = chain_id

    async def fetch_receipt(self, transaction_hash: str) -> AttributeDict:
        """Fetches the transaction receipt for a given transaction hash."""
        return

    async def fetch_transfer_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[Union[SendToChain, ReceiveFromChain]]:
        """Fetches cross-chain transfer events emitted from given contract, for a given block range."""

        if self.chain_id == constant.TEST_DEST_CHAIN_ID:
            # Mocking a destination chain
            if contract == settings.evm_wormhole_bridge:
                receive_from_chain_event = ReceiveFromChain(
                    emitter_address=contract,
                    block_number=from_block,
                    block_hash=constant.WH_DEST_BLOCK_HASH,
                    transaction_hash=constant.WH_DEST_TX_HASH,
                    source_chain_id=constant.WH_SRC_CHAIN_ID,
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
                    source_chain_id=constant.LZ_SRC_CHAIN_ID,
                    dest_chain_id=constant.LZ_DEST_CHAIN_ID,
                    amount=constant.TEST_AMOUNT,
                    message_id=constant.TEST_MESSAGE_ID,
                    to_address=constant.TEST_TO_ADDRESS,
                )
            return [receive_from_chain_event]
        return []

    async def fetch_mint_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[Mint]:
        """Fetches mint events emitted from given contract, for a given block range."""
        return []

    async def fetch_latest_block_number(self) -> int:
        """Fetches the latest block number."""

        return constant.TEST_BLOCK_NUMBER


class MockEvmClientSrcOnly(IEvmClient):
    def __init__(self, result: EvmResult, chain_id: int) -> None:
        self.result = result
        self.chain_id = chain_id

    async def fetch_receipt(self, transaction_hash: str) -> AttributeDict:
        """Fetches the transaction receipt for a given transaction hash."""
        return

    async def fetch_transfer_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[Union[SendToChain, ReceiveFromChain]]:
        """Fetches cross-chain transfer events emitted from given contract, for a given block range."""

        if self.chain_id == constant.TEST_SRC_CHAIN_ID:
            # Mocking a source chain
            if contract == settings.evm_wormhole_bridge:
                send_to_chain_event = SendToChain(
                    emitter_address=contract,
                    block_number=from_block,
                    block_hash=constant.WH_SRC_BLOCK_HASH,
                    transaction_hash=constant.WH_SRC_TX_HASH,
                    source_chain_id=constant.WH_SRC_CHAIN_ID,
                    dest_chain_id=constant.WH_DEST_CHAIN_ID,
                    amount=constant.TEST_AMOUNT,
                    message_id=constant.TEST_MESSAGE_ID,
                    from_address=constant.TEST_FROM_ADDRESS,
                )
            else:
                send_to_chain_event = SendToChain(
                    emitter_address=contract,
                    block_number=from_block,
                    block_hash=constant.LZ_SRC_BLOCK_HASH,
                    transaction_hash=constant.LZ_SRC_TX_HASH,
                    source_chain_id=constant.LZ_SRC_CHAIN_ID,
                    dest_chain_id=constant.LZ_DEST_CHAIN_ID,
                    amount=constant.TEST_AMOUNT,
                    message_id=constant.TEST_MESSAGE_ID,
                    from_address=constant.TEST_FROM_ADDRESS,
                )
            return [send_to_chain_event]
        return []

    async def fetch_mint_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[Mint]:
        """Fetches mint events emitted from given contract, for a given block range."""
        return []

    async def fetch_latest_block_number(self) -> int:
        """Fetches the latest block number."""

        return constant.TEST_BLOCK_NUMBER


class MockEvmClientBlockRange(IEvmClient):
    def __init__(
        self, result: EvmResult, greater_than_max_range: bool, chain_id: int
    ) -> None:
        self.result = result
        self.chain_id = chain_id
        self.greater_than_max_range = greater_than_max_range

    async def fetch_receipt(self, transaction_hash: str) -> AttributeDict:
        """Fetches the transaction receipt for a given transaction hash."""
        return

    async def fetch_transfer_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[Union[SendToChain, ReceiveFromChain]]:
        """Fetches cross-chain transfer events emitted from given contract, for a given block range."""

        return []

    async def fetch_mint_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[Mint]:
        """Fetches mint events emitted from given contract, for a given block range."""
        return []

    async def fetch_latest_block_number(self) -> int:
        """Fetches the latest block number."""

        last_stored = constant.TEST_BLOCK_NUMBER

        from_block = last_stored + 1

        if self.greater_than_max_range:
            # We should assert that to_block is max_possible_to_block
            latest_block = (
                from_block
                + CHAIN_DATA[self.chain_id]["query_size"]
                * constant.TEST_MAX_RANGE_MULTIPLIER
            )
            return latest_block
        # We should assert that to_block is latest_block minus 1
        latest_block = from_block + CHAIN_DATA[self.chain_id]["query_size"]
        return latest_block
