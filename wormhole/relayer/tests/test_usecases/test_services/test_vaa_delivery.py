# pylint: disable=unused-argument
# pylint: disable=duplicate-code
import json

import pytest
from databases import Database

import tests.constants as constant
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.interfaces.services.vaa_delivery import IVaaDelivery
from app.usecases.schemas.relays import Status


@pytest.mark.asyncio
async def test_deliver(
    vaa_delivery: IVaaDelivery,
    relays_repo: IRelaysRepo,
    test_db: Database,
    inserted_transaction: None,
) -> None:
    """Test that successful delivery of message gets properly handled"""
    mock_set_message = json.dumps(
        {
            "dest_chain_id": constant.TEST_DESTINATION_CHAIN_ID,
            "to_address": constant.TEST_USER_ADDRESS,
            "from_address": constant.TEST_USER_ADDRESS,
            "sequence": constant.TEST_SEQUENCE,
            "emitter_chain": constant.TEST_SOURCE_CHAIN_ID,
            "emitter_address": constant.TEST_EMITTER_ADDRESS,
            "vaa_hex": constant.TEST_VAA,
        }
    ).encode()

    # Process message
    await vaa_delivery.process(set_message=mock_set_message)

    # Assertions
    test_relay = await test_db.fetch_one(
        """SELECT * FROM transactions AS t JOIN relays AS r ON t.id = r.transaction_id 
        WHERE t.emitter_address=:emitter_address AND t.source_chain_id=:source_chain_id AND t.sequence=:sequence
        """,
        {
            "emitter_address": constant.TEST_EMITTER_ADDRESS,
            "source_chain_id": constant.TEST_SOURCE_CHAIN_ID,
            "sequence": constant.TEST_SEQUENCE,
        },
    )

    assert test_relay["status"] == Status.SUCCESS
    assert test_relay["error"] is None
    assert test_relay["transaction_hash"] == constant.TEST_TRANSACTION_HASH


@pytest.mark.asyncio
async def test_deliver_fail(
    vaa_delivery_fail: IVaaDelivery,
    relays_repo: IRelaysRepo,
    test_db: Database,
    inserted_transaction: None,
) -> None:
    """Test that failure to deliver message gets properly handled"""
    mock_set_message = json.dumps(
        {
            "dest_chain_id": constant.TEST_DESTINATION_CHAIN_ID,
            "to_address": constant.TEST_USER_ADDRESS,
            "from_address": constant.TEST_USER_ADDRESS,
            "sequence": constant.TEST_SEQUENCE,
            "emitter_chain": constant.TEST_SOURCE_CHAIN_ID,
            "emitter_address": constant.TEST_EMITTER_ADDRESS,
            "vaa_hex": constant.TEST_VAA,
        }
    ).encode()

    # Process message
    await vaa_delivery_fail.process(set_message=mock_set_message)

    # Assertions
    test_relay = await test_db.fetch_one(
        """SELECT * FROM transactions AS t JOIN relays AS r ON t.id = r.transaction_id 
        WHERE t.emitter_address=:emitter_address AND t.source_chain_id=:source_chain_id AND t.sequence=:sequence
        """,
        {
            "emitter_address": constant.TEST_EMITTER_ADDRESS,
            "source_chain_id": constant.TEST_SOURCE_CHAIN_ID,
            "sequence": constant.TEST_SEQUENCE,
        },
    )

    assert test_relay["status"] == Status.FAILED
    assert test_relay["error"] == constant.BLOCKCHAIN_CLIENT_ERROR_DETAIL
    assert test_relay["transaction_hash"] is None
