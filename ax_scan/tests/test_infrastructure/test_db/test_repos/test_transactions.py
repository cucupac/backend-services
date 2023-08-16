# pylint: disable=unused-argument
import pytest
from databases import Database

import tests.constants as constant
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.schemas.cross_chain_transaction import (
    CrossChainTransaction,
    CrossChainTxJoinEvmTx,
    UpdateCrossChainTransaction,
)
from app.usecases.schemas.evm_transaction import (
    EvmTransaction,
    EvmTransactionStatus,
    UpdateEvmTransaction,
)


@pytest.mark.asyncio
async def test_create_evm_tx(
    transactions_repo: ITransactionsRepo,
    test_db: Database,
    test_wh_evm_tx_src: EvmTransaction,
) -> None:
    evm_tx_id = await transactions_repo.create_evm_tx(evm_tx=test_wh_evm_tx_src)

    retrieved_evm_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.evm_transactions AS e_t WHERE e_t.id=:id""",
        {
            "id": evm_tx_id,
        },
    )

    for key, value in test_wh_evm_tx_src.model_dump().items():
        assert value == retrieved_evm_tx[key]


@pytest.mark.asyncio
async def test_create_cross_chain_tx(
    transactions_repo: ITransactionsRepo,
    test_db: Database,
    test_wh_cross_chain_tx_src_data: CrossChainTransaction,
) -> None:
    cross_chain_tx_id = await transactions_repo.create_cross_chain_tx(
        cross_chain_tx=test_wh_cross_chain_tx_src_data
    )

    retrieved_cross_chain_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.cross_chain_transactions AS c_c_t WHERE c_c_t.id=:id""",
        {
            "id": cross_chain_tx_id,
        },
    )

    for key, value in test_wh_cross_chain_tx_src_data.model_dump().items():
        assert value == retrieved_cross_chain_tx[key]


@pytest.mark.asyncio
async def test_update_cross_chain_tx(
    transactions_repo: ITransactionsRepo,
    test_db: Database,
    inserted_wh_evm_tx_dest: int,
    inserted_wh_cross_chain_tx_src_data: int,
) -> None:
    # Setup
    pre_update_cross_chain_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.cross_chain_transactions AS c_c_t WHERE c_c_t.id=:id""",
        {
            "id": inserted_wh_cross_chain_tx_src_data,
        },
    )

    assert pre_update_cross_chain_tx["dest_chain_tx_id"] is None

    # Act
    await transactions_repo.update_cross_chain_tx(
        cross_chain_tx_id=inserted_wh_cross_chain_tx_src_data,
        update_values=UpdateCrossChainTransaction(
            dest_chain_tx_id=inserted_wh_evm_tx_dest
        ),
    )

    post_update_cross_chain_tx = await test_db.fetch_one(
        """SELECT * FROM ax_scan.cross_chain_transactions AS c_c_t WHERE c_c_t.id=:id""",
        {
            "id": inserted_wh_cross_chain_tx_src_data,
        },
    )

    for key, value in dict(post_update_cross_chain_tx).items():
        if key == "dest_chain_tx_id":
            assert value == inserted_wh_evm_tx_dest
        elif key != "updated_at":
            assert value == pre_update_cross_chain_tx[key]


@pytest.mark.asyncio
async def test_retrieve_cross_chain_tx(
    transactions_repo: ITransactionsRepo,
    inserted_wh_cross_chain_tx_src_data: int,
) -> None:
    cross_chain_tx = await transactions_repo.retrieve_cross_chain_tx(
        chain_id=constant.TEST_SRC_CHAIN_ID, src_tx_hash=constant.WH_SRC_TX_HASH
    )

    assert isinstance(cross_chain_tx, CrossChainTxJoinEvmTx)
    assert cross_chain_tx.source_chain_id == constant.TEST_SRC_CHAIN_ID
    assert cross_chain_tx.dest_chain_id == constant.TEST_DEST_CHAIN_ID
    assert cross_chain_tx.from_address == constant.TEST_FROM_ADDRESS
    assert cross_chain_tx.to_address is None
    assert cross_chain_tx.amount == constant.TEST_AMOUNT
    assert cross_chain_tx.source_chain_tx_status == EvmTransactionStatus.PENDING
    assert cross_chain_tx.dest_chain_tx_status == EvmTransactionStatus.PENDING


@pytest.mark.asyncio
async def test_retrieve_pending(
    mixed_status_evm_txs: None,
    transactions_repo: ITransactionsRepo,
) -> None:
    """Tests that only pending transactions are retreived."""
    retrieved_evm_txs = await transactions_repo.retrieve_pending(
        chain_id=constant.TEST_SRC_CHAIN_ID
    )

    assert len(retrieved_evm_txs) == 2
    for tx in retrieved_evm_txs:
        assert tx.status == EvmTransactionStatus.PENDING


@pytest.mark.asyncio
async def test_update_evm_tx(
    inserted_wh_evm_tx_src: int,
    transactions_repo: ITransactionsRepo,
    test_db: Database,
) -> None:
    """Tests that an evm transaction is updated properly."""

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
    await transactions_repo.update_evm_tx(
        evm_tx_id=inserted_wh_evm_tx_src,
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
            "id": inserted_wh_evm_tx_src,
        },
    )

    assert retrieved_evm_tx["status"] == EvmTransactionStatus.SUCCESS
    assert retrieved_evm_tx["gas_price"] == constant.TEST_GAS_PRICE
    assert retrieved_evm_tx["gas_used"] == constant.TEST_GAS_USED
    assert retrieved_evm_tx["error"] is None
