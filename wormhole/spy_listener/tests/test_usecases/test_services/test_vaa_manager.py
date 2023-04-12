# pylint: disable=unused-argument
import codecs

import pytest
from databases import Database

import tests.constants as constant
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.interfaces.services.vaa_manager import IVaaManager
from app.usecases.schemas.relays import Status
from app.usecases.schemas.vaa import ParsedPayload, ParsedVaa


@pytest.mark.asyncio
async def test_publish_success(
    vaa_manager: IVaaManager,
    transactions_repo: ITransactionsRepo,
    test_db: Database,
) -> None:
    """Test that successful publishing of message gets properly handled."""
    # Setup
    test_parsed_vaa: ParsedVaa = vaa_manager.parse_vaa(vaa=constant.TEST_VAA_BYTES)

    # Action
    await vaa_manager.process(vaa=constant.TEST_VAA_BYTES)

    # Assertions
    # The message was stored in the database with correct information
    test_transaction = await test_db.fetch_one(
        """SELECT * FROM transactions AS t JOIN relays AS r ON t.id = r.transaction_id 
        WHERE t.emitter_address=:emitter_address AND t.source_chain_id=:source_chain_id AND t.sequence=:sequence
        """,
        {
            "emitter_address": test_parsed_vaa.emitter_address,
            "source_chain_id": test_parsed_vaa.emitter_chain,
            "sequence": test_parsed_vaa.sequence,
        },
    )

    assert test_transaction["emitter_address"] == test_parsed_vaa.emitter_address
    assert test_transaction["from_address"] == test_parsed_vaa.payload.from_address
    assert test_transaction["to_address"] == test_parsed_vaa.payload.to_address
    assert test_transaction["source_chain_id"] == test_parsed_vaa.emitter_chain
    assert test_transaction["dest_chain_id"] == test_parsed_vaa.payload.dest_chain_id
    assert test_transaction["amount"] == test_parsed_vaa.payload.amount
    assert test_transaction["sequence"] == test_parsed_vaa.sequence
    assert test_transaction["status"] == Status.PENDING
    assert not test_transaction["error"]
    assert (
        test_transaction["message"]
        == codecs.encode(bytes(constant.TEST_VAA_BYTES), "hex_codec").decode()
    )


@pytest.mark.asyncio
async def test_publish_fail(
    vaa_manager_unique_set_fail: IVaaManager,
    transactions_repo: ITransactionsRepo,
    test_db: Database,
) -> None:
    """Test that failure to publish message gets properly handled"""

    # Setup
    test_parsed_vaa: ParsedVaa = vaa_manager_unique_set_fail.parse_vaa(
        vaa=constant.TEST_VAA_BYTES
    )

    # Action
    await vaa_manager_unique_set_fail.process(vaa=constant.TEST_VAA_BYTES)

    # Assertions
    # The message was stored in the database with correct information
    test_transaction = await test_db.fetch_one(
        """SELECT * FROM transactions AS t JOIN relays AS r ON t.id = r.transaction_id 
        WHERE t.emitter_address=:emitter_address AND t.source_chain_id=:source_chain_id AND t.sequence=:sequence
        """,
        {
            "emitter_address": test_parsed_vaa.emitter_address,
            "source_chain_id": test_parsed_vaa.emitter_chain,
            "sequence": test_parsed_vaa.sequence,
        },
    )

    assert test_transaction["emitter_address"] == test_parsed_vaa.emitter_address
    assert test_transaction["from_address"] == test_parsed_vaa.payload.from_address
    assert test_transaction["to_address"] == test_parsed_vaa.payload.to_address
    assert test_transaction["source_chain_id"] == test_parsed_vaa.emitter_chain
    assert test_transaction["dest_chain_id"] == test_parsed_vaa.payload.dest_chain_id
    assert test_transaction["amount"] == test_parsed_vaa.payload.amount
    assert test_transaction["sequence"] == test_parsed_vaa.sequence
    assert test_transaction["status"] == Status.FAILED
    assert test_transaction["error"] == constant.UNIQUE_SET_ERROR_DETAIL
    assert (
        test_transaction["message"]
        == codecs.encode(bytes(constant.TEST_VAA_BYTES), "hex_codec").decode()
    )


@pytest.mark.asyncio
async def test_parse_vaa(vaa_manager: IVaaManager) -> None:
    test_parsed_vaa = vaa_manager.parse_vaa(vaa=constant.TEST_VAA_BYTES)

    assert isinstance(test_parsed_vaa, ParsedVaa)


@pytest.mark.asyncio
async def test_parse_payload(vaa_manager: IVaaManager) -> None:
    test_parsed_vaa = vaa_manager.parse_payload(payload=constant.TEST_VAA_PAYLOAD)

    assert isinstance(test_parsed_vaa, ParsedPayload)
