# pylint: disable=unused-argument
import pytest
from databases import Database

from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.schemas.cross_chain_transaction import (
    CrossChainTransaction,
    UpdateCrossChainTransaction,
)
from app.usecases.schemas.evm_transaction import (
    EvmTransaction,
    EvmTransactionInDb,
    EvmTransactionStatus,
    UpdateEvmTransaction,
)
import tests.constants as constant


@pytest.mark.asyncio
async def test_create_evm_tx(
    transactions_repo: ITransactionsRepo,
    test_db: Database,
    test_wh_evm_tx: EvmTransaction,
) -> None:
    evm_tx_id = await transactions_repo.create_evm_tx(evm_tx=test_wh_evm_tx)

    retrieved_evm_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.evm_transactions AS e_t WHERE e_t.id=:id""",
        {
            "id": evm_tx_id,
        },
    )

    for key, value in test_wh_evm_tx.model_dump().items():
        assert value == retrieved_evm_tx[key]


@pytest.mark.asyncio
async def test_create_cross_chain_tx(
    transactions_repo: ITransactionsRepo,
    test_db: Database,
    test_wh_cross_chain_tx: CrossChainTransaction,
) -> None:
    cross_chain_tx_id = await transactions_repo.create_cross_chain_tx(
        cross_chain_tx=test_wh_cross_chain_tx
    )

    retrieved_cross_chain_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.cross_chain_transactions AS c_c_t WHERE c_c_t.id=:id""",
        {
            "id": cross_chain_tx_id,
        },
    )

    for key, value in test_wh_cross_chain_tx.model_dump().items():
        assert value == retrieved_cross_chain_tx[key]


@pytest.mark.asyncio
async def test_update_cross_chain_tx(
    transactions_repo: ITransactionsRepo,
    test_db: Database,
    inserted_wh_dest_evm_transaction: int,
    inserted_wh_cross_chain_tx: int,
) -> None:
    # Setup
    pre_update_cross_chain_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.cross_chain_transactions AS c_c_t WHERE c_c_t.id=:id""",
        {
            "id": inserted_wh_cross_chain_tx,
        },
    )

    assert pre_update_cross_chain_tx["dest_chain_tx_id"] is None

    # Act
    await transactions_repo.update_cross_chain_tx(
        cross_chain_tx_id=inserted_wh_cross_chain_tx,
        update_values=UpdateCrossChainTransaction(
            dest_chain_tx_id=inserted_wh_dest_evm_transaction
        ),
    )

    post_update_cross_chain_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.cross_chain_transactions AS c_c_t WHERE c_c_t.id=:id""",
        {
            "id": inserted_wh_cross_chain_tx,
        },
    )

    for key, value in dict(post_update_cross_chain_tx).items():
        if key == "dest_chain_tx_id":
            assert value == inserted_wh_dest_evm_transaction
        elif key != "updated_at":
            assert value == pre_update_cross_chain_tx[key]


@pytest.mark.asyncio
async def test_retrieve_last_transaction(
    inserted_wh_evm_transaction: int,
    inserted_lz_evm_transaction: int,
    test_db: Database,
    transactions_repo: ITransactionsRepo,
) -> None:
    retrieved_evm_txs = await test_db.fetch_all(
        """SELECT * FROM ax_scan.evm_transactions AS evm_txs WHERE evm_txs.chain_id=:chain_id""",
        {
            "chain_id": constant.TEST_SOURCE_CHAIN_ID,
        },
    )

    retrieved_evm_tx = await transactions_repo.retrieve_last_transaction(
        chain_id=constant.TEST_SOURCE_CHAIN_ID
    )

    # Sort the retrieved transactions in descending order of block_number
    retrieved_evm_txs.sort(key=lambda tx: tx.block_number, reverse=True)

    assert retrieved_evm_tx == EvmTransactionInDb(**retrieved_evm_txs[0])


@pytest.mark.asyncio
async def test_retrieve_pending(
    mixed_status_evm_transactions: None,
    transactions_repo: ITransactionsRepo,
) -> None:
    """Tests that only pending transactions are retreived."""
    retrieved_evm_txs = await transactions_repo.retrieve_pending(
        chain_id=constant.TEST_SOURCE_CHAIN_ID
    )

    assert len(retrieved_evm_txs) == 2
    for tx in retrieved_evm_txs:
        assert tx.status == EvmTransactionStatus.PENDING


@pytest.mark.asyncio
async def test_update_evm_tx(
    inserted_wh_evm_transaction: int,
    transactions_repo: ITransactionsRepo,
    test_db: Database,
) -> None:
    """Tests that an evm transaction is updated properly."""

    # Pre-action assertions
    retrieved_evm_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.evm_transactions AS evm_txs WHERE evm_txs.id=:id""",
        {
            "id": inserted_wh_evm_transaction,
        },
    )

    assert retrieved_evm_tx["status"] == EvmTransactionStatus.PENDING
    assert retrieved_evm_tx["gas_price"] is None
    assert retrieved_evm_tx["gas_used"] is None
    assert retrieved_evm_tx["error"] is None

    # Act
    await transactions_repo.update_evm_tx(
        evm_tx_id=inserted_wh_evm_transaction,
        update_values=UpdateEvmTransaction(
            status=EvmTransactionStatus.SUCCESS,
            gas_price=constant.TEST_GAS_PRICE,
            gas_used=constant.TEST_GAS_USED,
            error=None,
        ),
    )

    # Post-action assertions
    retrieved_evm_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.evm_transactions AS evm_txs WHERE evm_txs.id=:id""",
        {
            "id": inserted_wh_evm_transaction,
        },
    )

    assert retrieved_evm_tx["status"] == EvmTransactionStatus.SUCCESS
    assert retrieved_evm_tx["gas_price"] == constant.TEST_GAS_PRICE
    assert retrieved_evm_tx["gas_used"] == constant.TEST_GAS_USED
    assert retrieved_evm_tx["error"] is None
