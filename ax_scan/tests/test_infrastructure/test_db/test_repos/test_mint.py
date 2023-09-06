# pylint: disable=unused-argument
import pytest
from databases import Database

import tests.constants as constant
from app.usecases.interfaces.repos.mints import IMintsRepo
from app.usecases.schemas.mints import MintData


@pytest.mark.asyncio
async def test_create(
    mints_repo: IMintsRepo, test_db: Database, inserted_mint_tx: int
) -> None:
    """Tests that a mint is creacted correctly."""

    mint_records = await test_db.fetch_all("""SELECT * FROM ax_scan.mints""")

    assert len(mint_records) == 0

    # Act
    await mints_repo.create(
        tx_id=inserted_mint_tx,
        mint_data=MintData(
            account=constant.TEST_MINT_MINTER, amount=constant.TEST_MINT_AMOUNT
        ),
    )

    mint_records = await test_db.fetch_all("""SELECT * FROM ax_scan.mints""")

    assert len(mint_records) == 1

    assert mint_records[0]["chain_tx_id"] == inserted_mint_tx
    assert mint_records[0]["account"] == constant.TEST_MINT_MINTER
    assert mint_records[0]["amount"] == constant.TEST_MINT_AMOUNT
