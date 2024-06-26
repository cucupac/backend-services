import pytest
from databases import Database

import tests.constants as constant
from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.interfaces.tasks.retry_failed import IRetryFailedTask
from app.usecases.schemas.relays import RelayErrors, Status
from app.usecases.schemas.tasks import TaskName


@pytest.mark.asyncio
async def test_task(
    retry_failed_task: IRetryFailedTask,
    test_db: Database,
    failed_transaction: None,  # pylint: disable = unused-argument
    tasks_repo: ITasksRepo,
) -> None:
    """Test that a missed-vaa, failed transaction is caught and properly relayed."""

    test_relay = await test_db.fetch_one(
        """SELECT * FROM wh_relayer.transactions AS t JOIN wh_relayer.relays AS r ON t.id = r.transaction_id
        WHERE t.emitter_address=:emitter_address AND t.source_chain_id=:source_chain_id AND t.sequence=:sequence
        """,
        {
            "emitter_address": constant.TEST_EMITTER_ADDRESS,
            "source_chain_id": constant.TEST_SOURCE_CHAIN_ID,
            "sequence": constant.TEST_SEQUENCE,
        },
    )

    assert test_relay["status"] == Status.FAILED
    assert test_relay["error"] == RelayErrors.MISSED_VAA
    assert test_relay["message"] is None
    assert test_relay["amount"] is None
    assert test_relay["to_address"] is None
    assert test_relay["from_address"] is None

    task = await tasks_repo.retrieve(task_name=TaskName.RETRY_FAILED)
    await retry_failed_task.task(task_id=task.id)

    test_relay = await test_db.fetch_one(
        """SELECT * FROM wh_relayer.transactions AS t JOIN wh_relayer.relays AS r ON t.id = r.transaction_id
        WHERE t.emitter_address=:emitter_address AND t.source_chain_id=:source_chain_id AND t.sequence=:sequence
        """,
        {
            "emitter_address": constant.TEST_EMITTER_ADDRESS,
            "source_chain_id": constant.TEST_SOURCE_CHAIN_ID,
            "sequence": constant.TEST_SEQUENCE,
        },
    )

    assert test_relay["status"] == Status.PENDING
    assert test_relay["error"] is None
    assert test_relay["message"] == constant.TEST_VAA
    assert test_relay["amount"] == constant.TEST_AMOUNT
    assert int(test_relay["to_address"], 16) == int(constant.TEST_USER_ADDRESS, 16)
    assert int(test_relay["from_address"], 16) == int(constant.TEST_USER_ADDRESS, 16)
    assert test_relay["transaction_hash"] == constant.TEST_TRANSACTION_HASH
