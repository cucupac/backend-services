# pylint: disable=unused-argument
import pytest
from databases import Database

from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.schemas.cross_chain_transaction import (
    CrossChainTransaction,
    UpdateCrossChainTransaction,
)
from app.usecases.schemas.evm_transaction import EvmTransaction


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
