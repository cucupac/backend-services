import pytest
from databases import Database

from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.interfaces.tasks.verify_delivery import IVerifyDeliveryTask
from app.usecases.schemas.blockchain import BlockchainErrors
from app.usecases.schemas.relays import Status
from app.usecases.schemas.tasks import TaskName


@pytest.mark.asyncio
async def test_task_success(
    verify_delivery_task_success: IVerifyDeliveryTask,
    test_db: Database,
    pending_transactions_with_tx_hash: None,  # pylint: disable = unused-argument
    tasks_repo: ITasksRepo,
) -> None:
    """Test that the verify_delivery task correctly updates relays with a 'pending' status and a transaction hash."""

    composite_ids = []

    test_undelivered_txs = await test_db.fetch_all(
        """SELECT * FROM wh_relayer.transactions AS t JOIN wh_relayer.relays AS r ON t.id = r.transaction_id
            WHERE r.status=:status AND r.transaction_hash IS NOT NULL""",
        {"status": Status.PENDING},
    )

    for tx in test_undelivered_txs:
        assert tx["status"] == Status.PENDING

        composite_ids.append(
            {
                "emitter_address": tx["emitter_address"],
                "source_chain_id": tx["source_chain_id"],
                "sequence": tx["sequence"],
            }
        )

    # Act
    task = await tasks_repo.retrieve(task_name=TaskName.VERIFY_DELIVERY)
    await verify_delivery_task_success.task(task_id=task.id)

    for composite_id in composite_ids:
        test_tx = await test_db.fetch_one(
            """SELECT * FROM wh_relayer.transactions AS t JOIN wh_relayer.relays AS r ON t.id = r.transaction_id
            WHERE t.emitter_address=:emitter_address AND t.source_chain_id=:source_chain_id AND t.sequence=:sequence
            """,
            {
                "emitter_address": composite_id["emitter_address"],
                "source_chain_id": composite_id["source_chain_id"],
                "sequence": composite_id["sequence"],
            },
        )

        assert test_tx["status"] == Status.SUCCESS
        assert test_tx["error"] is None
        assert test_tx["transaction_hash"] is not None


@pytest.mark.asyncio
async def test_task_fail(
    verify_delivery_task_fail: IVerifyDeliveryTask,
    test_db: Database,
    tasks_repo: ITasksRepo,
    pending_transactions_with_tx_hash: None,  # pylint: disable = unused-argument
) -> None:
    """Test that the verify_delivery task correctly updates relays with a 'pending' status and a transaction hash."""

    composite_ids = []

    test_undelivered_txs = await test_db.fetch_all(
        """SELECT * FROM wh_relayer.transactions AS t JOIN wh_relayer.relays AS r ON t.id = r.transaction_id
            WHERE r.status=:status AND r.transaction_hash IS NOT NULL""",
        {"status": Status.PENDING},
    )

    for tx in test_undelivered_txs:
        assert tx["status"] == Status.PENDING

        composite_ids.append(
            {
                "emitter_address": tx["emitter_address"],
                "source_chain_id": tx["source_chain_id"],
                "sequence": tx["sequence"],
            }
        )

    # Act
    task = await tasks_repo.retrieve(task_name=TaskName.VERIFY_DELIVERY)
    await verify_delivery_task_fail.task(task_id=task.id)

    for composite_id in composite_ids:
        test_tx = await test_db.fetch_one(
            """SELECT * FROM wh_relayer.transactions AS t JOIN wh_relayer.relays AS r ON t.id = r.transaction_id
            WHERE t.emitter_address=:emitter_address AND t.source_chain_id=:source_chain_id AND t.sequence=:sequence
            """,
            {
                "emitter_address": composite_id["emitter_address"],
                "source_chain_id": composite_id["source_chain_id"],
                "sequence": composite_id["sequence"],
            },
        )

        assert test_tx["status"] == Status.FAILED
        assert test_tx["error"] == BlockchainErrors.TX_RECEIPT_STATUS_NOT_ONE


@pytest.mark.asyncio
async def test_task_error(
    verify_delivery_task_error: IVerifyDeliveryTask,
    test_db: Database,
    pending_transactions_with_tx_hash: None,  # pylint: disable = unused-argument
    tasks_repo: ITasksRepo,
) -> None:
    """Test that the verify_delivery task correctly updates relays with a 'pending' status and a transaction hash."""

    composite_ids = []

    test_undelivered_txs = await test_db.fetch_all(
        """SELECT * FROM wh_relayer.transactions AS t JOIN wh_relayer.relays AS r ON t.id = r.transaction_id
            WHERE r.status=:status AND r.transaction_hash IS NOT NULL""",
        {"status": Status.PENDING},
    )

    for tx in test_undelivered_txs:
        assert tx["status"] == Status.PENDING

        composite_ids.append(
            {
                "emitter_address": tx["emitter_address"],
                "source_chain_id": tx["source_chain_id"],
                "sequence": tx["sequence"],
            }
        )

    # Act
    task = await tasks_repo.retrieve(task_name=TaskName.VERIFY_DELIVERY)
    await verify_delivery_task_error.task(task_id=task.id)

    for composite_id in composite_ids:
        test_tx = await test_db.fetch_one(
            """SELECT * FROM wh_relayer.transactions AS t JOIN wh_relayer.relays AS r ON t.id = r.transaction_id
            WHERE t.emitter_address=:emitter_address AND t.source_chain_id=:source_chain_id AND t.sequence=:sequence
            """,
            {
                "emitter_address": composite_id["emitter_address"],
                "source_chain_id": composite_id["source_chain_id"],
                "sequence": composite_id["sequence"],
            },
        )

        assert test_tx["status"] == Status.FAILED
        assert test_tx["error"] == BlockchainErrors.TX_HASH_NOT_IN_CHAIN
