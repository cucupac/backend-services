import codecs

import pytest
from databases import Database

import tests.constants as constant
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.interfaces.services.vaa_manager import IVaaManager
from app.usecases.schemas.vaa import ParsedPayload, ParsedVaa


@pytest.mark.asyncio
async def test_process(
    vaa_manager: IVaaManager, transactions_repo: ITransactionsRepo, test_db: Database
) -> None:

    test_parsed_vaa: ParsedVaa = vaa_manager._parse_vaa(vaa=constant.TEST_VAA_BYTES)

    await vaa_manager.process(vaa=constant.TEST_VAA_BYTES)

    # 1. The message was placed on the queue
    # TODO:

    # 2. The message was stored in the database
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
    assert test_transaction["status"]
    assert not test_transaction["error"]
    assert (
        test_transaction["message"]
        == codecs.encode(bytes(constant.TEST_VAA_BYTES), "hex_codec").decode()
    )


# @pytest.mark.asyncio
# async def test_process_unqueued(
#     vaa_manager: IVaaManager  # Need a different vaa_manager... -> vaa_manager_with_mock
# ) -> None:

#     await vaa_manager.process(vaa=constant.TEST_VAA_BYTES)

#     # 1. We'll mock the queue


#     # 2. The message was stored in the database


@pytest.mark.asyncio
async def test_parse_vaa(vaa_manager: IVaaManager) -> None:

    test_parsed_vaa = vaa_manager._parse_vaa(vaa=constant.TEST_VAA_BYTES)

    assert isinstance(test_parsed_vaa, ParsedVaa)


@pytest.mark.asyncio
async def test_parse_payload(vaa_manager: IVaaManager) -> None:

    test_parsed_vaa = vaa_manager._parse_payload(payload=constant.TEST_VAA_PAYLOAD)

    assert isinstance(test_parsed_vaa, ParsedPayload)
