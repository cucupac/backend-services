# pylint: disable=unused-argument
import pytest
from databases import Database

import tests.constants as constant
from app.usecases.interfaces.repos.points import IPointsRepo
from app.usecases.schemas.points import PointsInDb


@pytest.mark.asyncio
async def test_create(points_repo: IPointsRepo, test_db: Database) -> None:
    """Tests that points are upserted correctly."""

    # Setup
    points_create_amount = 1000

    point_records = await test_db.fetch_all("""SELECT * FROM ax_scan.points""")

    assert len(point_records) == 0

    # Act
    await points_repo.create(
        account=constant.TEST_MINT_MINTER, points=points_create_amount
    )

    point_records = await test_db.fetch_all("""SELECT * FROM ax_scan.points""")

    assert len(point_records) == 1

    assert point_records[0]["account"] == constant.TEST_MINT_MINTER
    assert point_records[0]["points"] == points_create_amount


@pytest.mark.asyncio
async def test_update(points_repo: IPointsRepo, test_db: Database) -> None:
    """Tests that points are upserted correctly."""

    # Setup
    points_create_amount = 1000
    points_update_amount = 2000
    await points_repo.create(
        account=constant.TEST_MINT_MINTER, points=points_create_amount
    )

    # Act
    await points_repo.update(
        account=constant.TEST_MINT_MINTER, points=points_update_amount
    )

    point_records = await test_db.fetch_all("""SELECT * FROM ax_scan.points""")

    assert len(point_records) == 1

    assert point_records[0]["account"] == constant.TEST_MINT_MINTER
    assert point_records[0]["points"] == points_update_amount


@pytest.mark.asyncio
async def test_retrieve(points_repo: IPointsRepo) -> None:
    """Tests that points are retrieved correctly."""

    # Setup
    points_create_amount = 1000
    await points_repo.create(
        account=constant.TEST_MINT_MINTER, points=points_create_amount
    )

    # Act
    account_points = await points_repo.retrieve(account=constant.TEST_MINT_MINTER)

    assert isinstance(account_points, PointsInDb)

    assert account_points.account == constant.TEST_MINT_MINTER
    assert account_points.points == points_create_amount
