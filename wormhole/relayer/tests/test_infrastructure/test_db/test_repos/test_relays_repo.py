# pylint: disable=unused-argument
import pytest
from databases import Database

import tests.constants as constant
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.schemas.relays import Status, UpdateRepoAdapter


@pytest.mark.asyncio
async def test_update(
    relays_repo: IRelaysRepo,
    inserted_transaction: None,
    update_relays_repo_adapter: UpdateRepoAdapter,
    test_db: Database,
) -> None:
    """Test that relays table can be updated"""

    await relays_repo.update(relay=update_relays_repo_adapter)

    # Assertions
    test_relay = await test_db.fetch_one(
        """SELECT * FROM ax_relayer.transactions AS t JOIN ax_relayer.relays AS r ON t.id = r.transaction_id 
        WHERE t.emitter_address=:emitter_address AND t.source_chain_id=:source_chain_id AND t.sequence=:sequence
        """,
        {
            "emitter_address": constant.TEST_EMITTER_ADDRESS,
            "source_chain_id": constant.TEST_SOURCE_CHAIN_ID,
            "sequence": constant.TEST_SEQUENCE,
        },
    )

    assert test_relay["emitter_address"] == constant.TEST_EMITTER_ADDRESS
    assert test_relay["source_chain_id"] == constant.TEST_SOURCE_CHAIN_ID
    assert test_relay["sequence"] == constant.TEST_SEQUENCE
    assert test_relay["transaction_hash"] == constant.TEST_TRANSACTION_HASH
    assert test_relay["error"] is None
    assert test_relay["status"] == Status.SUCCESS
