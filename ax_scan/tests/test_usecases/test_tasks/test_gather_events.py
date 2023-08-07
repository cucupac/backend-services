import pytest
from databases import Database

import tests.constants as constant
from app.dependencies import CHAIN_DATA
from app.usecases.interfaces.tasks.gather_events import IGatherEventsTask
from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.schemas.tasks import TaskName
from app.usecases.schemas.evm_transaction import EvmTransactionStatus
from app.usecases.schemas.bridge import Bridges
from app.usecases.schemas.events import EmitterAddress


@pytest.mark.asyncio
async def test_task_insert(
    gather_events_task_insert: IGatherEventsTask,
    tasks_repo: ITasksRepo,
    test_db: Database,
) -> None:
    """Tests that the whole picture gets pieced together upon an insertion flow."""
    # Setup
    tested_chains = (constant.TEST_SOURCE_CHAIN_ID, constant.TEST_DEST_CHAIN_ID)
    evm_tx_ids = []
    cross_chain_tx_ids = []

    # Act
    task = await tasks_repo.retrieve(task_name=TaskName.GATHER_EVENTS)
    await gather_events_task_insert.task(task_id=task.id)

    retrieved_evm_txs = await test_db.fetch_all(
        """SELECT * FROM ax_scan.evm_transactions"""
    )

    retrieved_cross_chain_txs = await test_db.fetch_all(
        """SELECT * FROM ax_scan.cross_chain_transactions"""
    )

    retrieved_wh_messages = await test_db.fetch_all(
        """SELECT * FROM ax_scan.wormhole_messages"""
    )

    retrieved_lz_messages = await test_db.fetch_all(
        """SELECT * FROM ax_scan.layer_zero_messages"""
    )

    # evm_transactions assertions
    assert len(retrieved_evm_txs) == 4
    for evm_tx in retrieved_evm_txs:
        assert evm_tx["gas_price"] is None
        assert evm_tx["gas_used"] is None
        assert evm_tx["status"] == EvmTransactionStatus.PENDING
        assert evm_tx["error"] is None
        assert evm_tx["chain_id"] in tested_chains
        evm_tx_ids.append(evm_tx["id"])

    # cross_chain_transactions assertions
    assert len(retrieved_cross_chain_txs) == 2
    for cross_chain_tx in retrieved_cross_chain_txs:
        assert Bridges(cross_chain_tx["bridge"])
        assert cross_chain_tx["from_address"] == constant.TEST_FROM_ADDRESS
        assert cross_chain_tx["to_address"] == constant.TEST_TO_ADDRESS
        assert cross_chain_tx["source_chain_id"] == constant.TEST_SOURCE_CHAIN_ID
        assert cross_chain_tx["dest_chain_id"] == constant.TEST_DEST_CHAIN_ID
        assert cross_chain_tx["amount"] == constant.TEST_AMOUNT
        assert cross_chain_tx["source_chain_tx_id"] in evm_tx_ids
        assert cross_chain_tx["dest_chain_tx_id"] in evm_tx_ids
        cross_chain_tx_ids.append(cross_chain_tx["id"])

    # wormhole_messages assertions
    assert len(retrieved_wh_messages) == 1
    for wh_message in retrieved_wh_messages:
        assert wh_message["cross_chain_tx_id"] in cross_chain_tx_ids
        assert wh_message["emitter_address"] == EmitterAddress.WORMHOLE_BRIDGE
        assert wh_message["source_chain_id"] == constant.WH_SOURCE_CHAIN_ID
        assert wh_message["sequence"] == constant.TEST_MESSAGE_ID

    # layer_zero_messages assertions
    assert len(retrieved_lz_messages) == 1
    for lz_message in retrieved_lz_messages:
        assert lz_message["cross_chain_tx_id"] in cross_chain_tx_ids
        assert lz_message["emitter_address"] == EmitterAddress.LAYER_ZERO_BRIDGE
        assert lz_message["source_chain_id"] == constant.LZ_SOURCE_CHAIN_ID
        assert lz_message["dest_chain_id"] == constant.LZ_DEST_CHAIN_ID
        assert lz_message["nonce"] == constant.TEST_MESSAGE_ID


@pytest.mark.asyncio
async def test_task_update_wh(
    gather_events_task_update: IGatherEventsTask,
    tasks_repo: ITasksRepo,
    test_db: Database,
    inserted_wormhole_message: None,
) -> None:
    """Tests that the whole picture gets pieced together upon an insertion flow."""
    # Setup
    evm_tx_ids = {}
    cross_chain_tx_id = None

    retrieved_evm_txs = await test_db.fetch_all(
        """SELECT * FROM ax_scan.evm_transactions"""
    )

    retrieved_cross_chain_txs = await test_db.fetch_all(
        """SELECT * FROM ax_scan.cross_chain_transactions"""
    )

    retrieved_wh_messages = await test_db.fetch_all(
        """SELECT * FROM ax_scan.wormhole_messages"""
    )

    # [Pre-action]: evm_transactions assertions
    assert len(retrieved_evm_txs) == 1
    evm_tx_ids["source_chain_tx_id"] = retrieved_evm_txs[0]["id"]

    # [Pre-action]: cross_chain_transactions assertions (to_address and dest_chain_tx_id should be null)
    assert len(retrieved_cross_chain_txs) == 1
    for cross_chain_tx in retrieved_cross_chain_txs:
        for key, value in dict(cross_chain_tx).items():
            if key == "to_address" or key == "dest_chain_tx_id":
                assert value is None
            else:
                assert value is not None
        cross_chain_tx_id = cross_chain_tx["id"]

    # [Pre-action]: wormhole_messages assertions
    assert len(retrieved_wh_messages) == 1
    for wh_message in retrieved_wh_messages:
        assert wh_message["cross_chain_tx_id"] == cross_chain_tx_id
        assert wh_message["emitter_address"] == EmitterAddress.WORMHOLE_BRIDGE
        assert wh_message["source_chain_id"] == constant.WH_SOURCE_CHAIN_ID
        assert wh_message["sequence"] == constant.TEST_MESSAGE_ID

    # Act
    task = await tasks_repo.retrieve(task_name=TaskName.GATHER_EVENTS)
    await gather_events_task_update.task(task_id=task.id)

    retrieved_evm_txs = await test_db.fetch_all(
        """SELECT * FROM ax_scan.evm_transactions"""
    )

    updated_cross_chain_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.cross_chain_transactions AS c_c_t WHERE c_c_t.id=:id""",
        {"id": cross_chain_tx_id},
    )

    retrieved_wh_messages = await test_db.fetch_all(
        """SELECT * FROM ax_scan.wormhole_messages"""
    )

    # [Post-action]: cross_chain_transactions assertions (dest_chain_tx_id and to_address should be updated)
    assert Bridges(updated_cross_chain_tx["bridge"])
    assert updated_cross_chain_tx["from_address"] == constant.TEST_FROM_ADDRESS
    assert updated_cross_chain_tx["to_address"] == constant.TEST_TO_ADDRESS
    assert updated_cross_chain_tx["source_chain_id"] == constant.TEST_SOURCE_CHAIN_ID
    assert updated_cross_chain_tx["dest_chain_id"] == constant.TEST_DEST_CHAIN_ID
    assert updated_cross_chain_tx["amount"] == constant.TEST_AMOUNT
    assert (
        updated_cross_chain_tx["source_chain_tx_id"] == evm_tx_ids["source_chain_tx_id"]
    )
    assert updated_cross_chain_tx["dest_chain_tx_id"] is not None

    # [Post-action]: wormhole_messages assertions (it's the same message)
    assert len(retrieved_wh_messages) == 1
    for wh_message in retrieved_wh_messages:
        assert wh_message["cross_chain_tx_id"] == cross_chain_tx_id
        assert wh_message["emitter_address"] == EmitterAddress.WORMHOLE_BRIDGE
        assert wh_message["source_chain_id"] == constant.WH_SOURCE_CHAIN_ID
        assert wh_message["sequence"] == constant.TEST_MESSAGE_ID


@pytest.mark.asyncio
async def test_task_update_lz(
    gather_events_task_update: IGatherEventsTask,
    tasks_repo: ITasksRepo,
    test_db: Database,
    inserted_layer_zero_message: None,
) -> None:
    """Tests that the whole picture gets pieced together upon an insertion flow."""
    # Setup
    evm_tx_ids = {}
    cross_chain_tx_id = None

    retrieved_evm_txs = await test_db.fetch_all(
        """SELECT * FROM ax_scan.evm_transactions"""
    )

    retrieved_cross_chain_txs = await test_db.fetch_all(
        """SELECT * FROM ax_scan.cross_chain_transactions"""
    )

    retrieved_lz_messages = await test_db.fetch_all(
        """SELECT * FROM ax_scan.layer_zero_messages"""
    )

    # [Pre-action]: evm_transactions assertions
    assert len(retrieved_evm_txs) == 1
    evm_tx_ids["source_chain_tx_id"] = retrieved_evm_txs[0]["id"]

    # [Pre-action]: cross_chain_transactions assertions (to_address and dest_chain_tx_id should be null)
    assert len(retrieved_cross_chain_txs) == 1
    for cross_chain_tx in retrieved_cross_chain_txs:
        for key, value in dict(cross_chain_tx).items():
            if key == "to_address" or key == "dest_chain_tx_id":
                assert value is None
            else:
                assert value is not None
        cross_chain_tx_id = cross_chain_tx["id"]

    # [Pre-action]: layer_zero_message assertions
    assert len(retrieved_lz_messages) == 1
    for lz_message in retrieved_lz_messages:
        assert lz_message["cross_chain_tx_id"] == cross_chain_tx_id
        assert lz_message["emitter_address"] == EmitterAddress.LAYER_ZERO_BRIDGE
        assert lz_message["source_chain_id"] == constant.LZ_SOURCE_CHAIN_ID
        assert lz_message["dest_chain_id"] == constant.LZ_DEST_CHAIN_ID
        assert lz_message["nonce"] == constant.TEST_MESSAGE_ID

    # Act
    task = await tasks_repo.retrieve(task_name=TaskName.GATHER_EVENTS)
    await gather_events_task_update.task(task_id=task.id)

    retrieved_evm_txs = await test_db.fetch_all(
        """SELECT * FROM ax_scan.evm_transactions"""
    )

    updated_cross_chain_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.cross_chain_transactions AS c_c_t WHERE c_c_t.id=:id""",
        {"id": cross_chain_tx_id},
    )

    retrieved_lz_messages = await test_db.fetch_all(
        """SELECT * FROM ax_scan.layer_zero_messages"""
    )

    # [Post-action]: cross_chain_transactions assertions (dest_chain_tx_id and to_address should be updated)
    assert Bridges(updated_cross_chain_tx["bridge"])
    assert updated_cross_chain_tx["from_address"] == constant.TEST_FROM_ADDRESS
    assert updated_cross_chain_tx["to_address"] == constant.TEST_TO_ADDRESS
    assert updated_cross_chain_tx["source_chain_id"] == constant.TEST_SOURCE_CHAIN_ID
    assert updated_cross_chain_tx["dest_chain_id"] == constant.TEST_DEST_CHAIN_ID
    assert updated_cross_chain_tx["amount"] == constant.TEST_AMOUNT
    assert (
        updated_cross_chain_tx["source_chain_tx_id"] == evm_tx_ids["source_chain_tx_id"]
    )
    assert updated_cross_chain_tx["dest_chain_tx_id"] is not None

    # [Post-action]: layer_zero_message assertions (it's the same message)
    assert len(retrieved_lz_messages) == 1
    for lz_message in retrieved_lz_messages:
        assert lz_message["cross_chain_tx_id"] == cross_chain_tx_id
        assert lz_message["emitter_address"] == EmitterAddress.LAYER_ZERO_BRIDGE
        assert lz_message["source_chain_id"] == constant.LZ_SOURCE_CHAIN_ID
        assert lz_message["dest_chain_id"] == constant.LZ_DEST_CHAIN_ID
        assert lz_message["nonce"] == constant.TEST_MESSAGE_ID


@pytest.mark.asyncio
async def test_get_block_range_gt(
    gather_events_task_block_range_gt: IGatherEventsTask,
    transactions_repo: ITransactionsRepo,
    inserted_wormhole_message: None,
) -> None:
    """Tests the case where the on-chain block number exceeds the maximum, evm-allowed block range.
    This test uses the Wormhole source transaction block number as its last database-stored block number.
    """

    # Setup
    last_stored_tx = await transactions_repo.retrieve_last_transaction(
        chain_id=constant.TEST_SOURCE_CHAIN_ID
    )

    assert last_stored_tx.block_number == constant.WH_SOURCE_BLOCK_NUMBER

    test_from_block = last_stored_tx.block_number + 1

    max_possible_to_block = (
        test_from_block + CHAIN_DATA[constant.TEST_SOURCE_CHAIN_ID]["max_block_range"]
    )

    # Act
    block_range = await gather_events_task_block_range_gt.get_block_range(
        ax_chain_id=constant.TEST_SOURCE_CHAIN_ID
    )

    # Assertions
    assert block_range.from_block == test_from_block
    assert block_range.to_block == max_possible_to_block


@pytest.mark.asyncio
async def test_get_block_range_lt(
    gather_events_task_block_range_lt: IGatherEventsTask,
    transactions_repo: ITransactionsRepo,
    inserted_wormhole_message: None,
) -> None:
    """Tests the case where the on-chain block number is less than the maximum, evm-allowed upper bound.
    This test uses the Wormhole source transaction block number as its last database-stored block number.
    """

    # Setup
    last_stored_tx = await transactions_repo.retrieve_last_transaction(
        chain_id=constant.TEST_SOURCE_CHAIN_ID
    )

    assert last_stored_tx.block_number == constant.WH_SOURCE_BLOCK_NUMBER

    test_from_block = last_stored_tx.block_number + 1

    on_chain_latest = (
        last_stored_tx.block_number
        + CHAIN_DATA[constant.TEST_SOURCE_CHAIN_ID]["max_block_range"]
        + 1
    )

    max_uppoer_bound = on_chain_latest - 1

    # Act
    block_range = await gather_events_task_block_range_lt.get_block_range(
        ax_chain_id=constant.TEST_SOURCE_CHAIN_ID
    )

    # Assertions
    assert block_range.from_block == test_from_block
    assert block_range.to_block == max_uppoer_bound
