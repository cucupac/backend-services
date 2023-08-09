import pytest
from databases import Database

import tests.constants as constant
from app.usecases.tasks.verify_transactions import IVerifyTransactionsTask
from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.schemas.evm_transaction import EvmTransactionStatus
from app.usecases.schemas.blockchain import BlockchainErrors
from app.usecases.schemas.tasks import TaskName


@pytest.mark.asyncio
async def test_task_successful(
    verify_transactions_task_found_status_is_one: IVerifyTransactionsTask,
    inserted_wh_evm_tx_src: int,
    tasks_repo: ITasksRepo,
    test_db: Database,
) -> None:
    """Tests that pending transactions get verified properly."""

    # Pre-action assertions
    retrieved_evm_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.evm_transactions AS evm_txs WHERE evm_txs.id=:id""",
        {
            "id": inserted_wh_evm_tx_src,
        },
    )

    assert retrieved_evm_tx["status"] == EvmTransactionStatus.PENDING
    assert retrieved_evm_tx["gas_price"] is None
    assert retrieved_evm_tx["gas_used"] is None
    assert retrieved_evm_tx["error"] is None

    # Act
    task = await tasks_repo.retrieve(task_name=TaskName.VERIFY_TRANSACTIONS)
    await verify_transactions_task_found_status_is_one.task(task_id=task.id)

    # Post-action assertions
    retrieved_evm_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.evm_transactions AS evm_txs WHERE evm_txs.id=:id""",
        {
            "id": inserted_wh_evm_tx_src,
        },
    )

    assert retrieved_evm_tx["status"] == EvmTransactionStatus.SUCCESS
    assert retrieved_evm_tx["gas_price"] == constant.TEST_GAS_PRICE
    assert retrieved_evm_tx["gas_used"] == constant.TEST_GAS_USED
    assert retrieved_evm_tx["error"] is None


@pytest.mark.asyncio
async def test_task_status_not_one(
    verify_transactions_task_found_status_not_one: IVerifyTransactionsTask,
    inserted_wh_evm_tx_src: int,
    tasks_repo: ITasksRepo,
    test_db: Database,
) -> None:
    """Tests that unsuccessful transactions get updated to failed."""

    # Pre-action assertions
    retrieved_evm_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.evm_transactions AS evm_txs WHERE evm_txs.id=:id""",
        {
            "id": inserted_wh_evm_tx_src,
        },
    )

    assert retrieved_evm_tx["status"] == EvmTransactionStatus.PENDING
    assert retrieved_evm_tx["gas_price"] is None
    assert retrieved_evm_tx["gas_used"] is None
    assert retrieved_evm_tx["error"] is None

    # Act
    task = await tasks_repo.retrieve(task_name=TaskName.VERIFY_TRANSACTIONS)
    await verify_transactions_task_found_status_not_one.task(task_id=task.id)

    # Post-action assertions
    retrieved_evm_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.evm_transactions AS evm_txs WHERE evm_txs.id=:id""",
        {
            "id": inserted_wh_evm_tx_src,
        },
    )

    assert retrieved_evm_tx["status"] == EvmTransactionStatus.FAILED
    assert retrieved_evm_tx["gas_price"] is None
    assert retrieved_evm_tx["gas_used"] is None
    assert retrieved_evm_tx["error"] == BlockchainErrors.TX_RECEIPT_STATUS_NOT_ONE


@pytest.mark.asyncio
async def test_task_not_found(
    verify_transactions_task_not_found: IVerifyTransactionsTask,
    inserted_wh_evm_tx_src: int,
    tasks_repo: ITasksRepo,
    test_db: Database,
) -> None:
    """Tests that unfound transactions get updated to failed."""

    # Pre-action assertions
    retrieved_evm_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.evm_transactions AS evm_txs WHERE evm_txs.id=:id""",
        {
            "id": inserted_wh_evm_tx_src,
        },
    )

    assert retrieved_evm_tx["status"] == EvmTransactionStatus.PENDING
    assert retrieved_evm_tx["gas_price"] is None
    assert retrieved_evm_tx["gas_used"] is None
    assert retrieved_evm_tx["error"] is None

    # Act
    task = await tasks_repo.retrieve(task_name=TaskName.VERIFY_TRANSACTIONS)
    await verify_transactions_task_not_found.task(task_id=task.id)

    # Post-action assertions
    retrieved_evm_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.evm_transactions AS evm_txs WHERE evm_txs.id=:id""",
        {
            "id": inserted_wh_evm_tx_src,
        },
    )

    assert retrieved_evm_tx["status"] == EvmTransactionStatus.FAILED
    assert retrieved_evm_tx["gas_price"] is None
    assert retrieved_evm_tx["gas_used"] is None
    assert retrieved_evm_tx["error"] == constant.NOT_FOUND_ERROR


@pytest.mark.asyncio
async def test_task_blockchain_client_error(
    verify_transactions_task_general_error: IVerifyTransactionsTask,
    inserted_wh_evm_tx_src: int,
    tasks_repo: ITasksRepo,
    test_db: Database,
) -> None:
    """Tests that database is updated properly upon a blockchain client error."""

    # Pre-action assertions
    retrieved_evm_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.evm_transactions AS evm_txs WHERE evm_txs.id=:id""",
        {
            "id": inserted_wh_evm_tx_src,
        },
    )

    assert retrieved_evm_tx["status"] == EvmTransactionStatus.PENDING
    assert retrieved_evm_tx["gas_price"] is None
    assert retrieved_evm_tx["gas_used"] is None
    assert retrieved_evm_tx["error"] is None

    # Act
    task = await tasks_repo.retrieve(task_name=TaskName.VERIFY_TRANSACTIONS)
    await verify_transactions_task_general_error.task(task_id=task.id)

    # Post-action assertions
    retrieved_evm_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.evm_transactions AS evm_txs WHERE evm_txs.id=:id""",
        {
            "id": inserted_wh_evm_tx_src,
        },
    )

    assert retrieved_evm_tx["status"] == EvmTransactionStatus.PENDING
    assert retrieved_evm_tx["gas_price"] is None
    assert retrieved_evm_tx["gas_used"] is None
    assert retrieved_evm_tx["error"] is None
