import pytest
from databases import Database

import tests.constants as constant
from app.settings import settings
from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.interfaces.tasks.gather_missed import IGatherMissedVaasTask
from app.usecases.schemas.relays import RelayErrors, Status
from app.usecases.schemas.tasks import TaskName


@pytest.mark.asyncio
async def test_task(
    gather_missed_task: IGatherMissedVaasTask,
    inserted_recent_transactions: None,  # pylint: disable = unused-argument
    test_db: Database,
    tasks_repo: ITasksRepo,
) -> None:
    """Test that missed VAAs are added to our database."""

    # Assert that test missed VAAs are not in the database
    for test_sequence in constant.TEST_MISSED_VAAS_CELO_SEQUENCES:
        test_relay = await test_db.fetch_one(
            """SELECT * FROM wh_relayer.transactions AS t JOIN wh_relayer.relays AS r ON t.id = r.transaction_id
            WHERE t.emitter_address=:emitter_address AND t.source_chain_id=:source_chain_id AND t.sequence=:sequence
            """,
            {
                "emitter_address": constant.TEST_EMITTER_ADDRESS,
                "source_chain_id": constant.CELO_CHAIN_ID,
                "sequence": test_sequence,
            },
        )
        assert not test_relay

    for test_sequence in constant.TEST_MISSED_VAAS_POLYGON_SEQUENCES:
        test_relay = await test_db.fetch_one(
            """SELECT * FROM wh_relayer.transactions AS t JOIN wh_relayer.relays AS r ON t.id = r.transaction_id
            WHERE t.emitter_address=:emitter_address AND t.source_chain_id=:source_chain_id AND t.sequence=:sequence
            """,
            {
                "emitter_address": constant.TEST_EMITTER_ADDRESS,
                "source_chain_id": constant.POLYGON_CHAIN_ID,
                "sequence": test_sequence,
            },
        )
        assert not test_relay

    # Act
    settings.evm_wormhole_bridge = constant.TEST_EMITTER_ADDRESS
    task = await tasks_repo.retrieve(task_name=TaskName.GATHER_MISSED)
    await gather_missed_task.task(task_id=task.id)

    # Assert that previously missing VAAs are now tracked
    for test_sequence in constant.TEST_MISSED_VAAS_CELO_SEQUENCES:
        test_relay = await test_db.fetch_one(
            """SELECT * FROM wh_relayer.transactions AS t JOIN wh_relayer.relays AS r ON t.id = r.transaction_id
            WHERE t.emitter_address=:emitter_address AND t.source_chain_id=:source_chain_id AND t.sequence=:sequence
            """,
            {
                "emitter_address": constant.TEST_EMITTER_ADDRESS,
                "source_chain_id": constant.CELO_CHAIN_ID,
                "sequence": test_sequence,
            },
        )

        assert test_relay["status"] == Status.FAILED
        assert test_relay["error"] == RelayErrors.MISSED_VAA
        assert test_relay["message"] == constant.MISSING_VAAS.get(
            constant.CELO_CHAIN_ID
        ).get(test_sequence).get("contract_payload")
        assert test_relay["amount"] == constant.TEST_AMOUNT
        assert int(test_relay["to_address"], 16) == int(constant.TEST_USER_ADDRESS, 16)
        assert int(test_relay["from_address"], 16) == int(
            constant.TEST_USER_ADDRESS, 16
        )
        assert test_relay["transaction_hash"] is None

    for test_sequence in constant.TEST_MISSED_VAAS_POLYGON_SEQUENCES:
        test_relay = await test_db.fetch_one(
            """SELECT * FROM wh_relayer.transactions AS t JOIN wh_relayer.relays AS r ON t.id = r.transaction_id
            WHERE t.emitter_address=:emitter_address AND t.source_chain_id=:source_chain_id AND t.sequence=:sequence
            """,
            {
                "emitter_address": constant.TEST_EMITTER_ADDRESS,
                "source_chain_id": constant.POLYGON_CHAIN_ID,
                "sequence": test_sequence,
            },
        )

        assert test_relay["status"] == Status.FAILED
        assert test_relay["error"] == RelayErrors.MISSED_VAA
        assert test_relay["message"] == constant.MISSING_VAAS.get(
            constant.POLYGON_CHAIN_ID
        ).get(test_sequence).get("contract_payload")
        assert test_relay["amount"] == constant.TEST_AMOUNT
        assert int(test_relay["to_address"], 16) == int(constant.TEST_USER_ADDRESS, 16)
        assert int(test_relay["from_address"], 16) == int(
            constant.TEST_USER_ADDRESS, 16
        )
        assert test_relay["transaction_hash"] is None
