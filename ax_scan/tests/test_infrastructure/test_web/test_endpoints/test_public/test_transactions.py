import pytest
from httpx import AsyncClient
from fastapi import HTTPException

import tests.constants as constant
from app.usecases.schemas.cross_chain_transaction import Status
from app.usecases.interfaces.repos.transactions import ITransactionsRepo


@pytest.mark.asyncio
async def test_get_transaction_pending(
    test_client: AsyncClient,
    transactions_repo: ITransactionsRepo,
    inserted_wormhole_message: None,
) -> None:
    endpoint = f"/public/transactions/{constant.TEST_SOURCE_CHAIN_ID}/{constant.WH_SOURCE_TX_HASH}"

    cross_chain_tx = await transactions_repo.retrieve_cross_chain_tx(
        chain_id=constant.TEST_SOURCE_CHAIN_ID, src_tx_hash=constant.WH_SOURCE_TX_HASH
    )

    # Test successful user creation
    response = await test_client.get(endpoint)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    for key, value in response_data.items():
        if key != "status":
            assert cross_chain_tx.model_dump()[key] == value
    assert response_data["status"] == Status.PENDING


@pytest.mark.asyncio
async def test_get_transaction_success(
    test_client: AsyncClient,
    transactions_repo: ITransactionsRepo,
    complete_successful_cross_chain_tx: None,
) -> None:
    endpoint = f"/public/transactions/{constant.TEST_SOURCE_CHAIN_ID}/{constant.WH_SOURCE_TX_HASH}"

    cross_chain_tx = await transactions_repo.retrieve_cross_chain_tx(
        chain_id=constant.TEST_SOURCE_CHAIN_ID, src_tx_hash=constant.WH_SOURCE_TX_HASH
    )

    # Test successful user creation
    response = await test_client.get(endpoint)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    for key, value in response_data.items():
        if key != "status":
            assert cross_chain_tx.model_dump()[key] == value
    assert response_data["status"] == Status.SUCCESS


@pytest.mark.asyncio
async def test_get_transaction_failed(
    test_client: AsyncClient,
    transactions_repo: ITransactionsRepo,
    failed_cross_chain_tx: None,
) -> None:
    endpoint = f"/public/transactions/{constant.TEST_SOURCE_CHAIN_ID}/{constant.WH_SOURCE_TX_HASH}"

    cross_chain_tx = await transactions_repo.retrieve_cross_chain_tx(
        chain_id=constant.TEST_SOURCE_CHAIN_ID, src_tx_hash=constant.WH_SOURCE_TX_HASH
    )

    # Test successful user creation
    response = await test_client.get(endpoint)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    for key, value in response_data.items():
        if key != "status":
            assert cross_chain_tx.model_dump()[key] == value
    assert response_data["status"] == Status.FAILED


@pytest.mark.asyncio
async def test_get_transaction_not_found(
    test_client: AsyncClient,
    transactions_repo: ITransactionsRepo,
    inserted_wormhole_message: None,
) -> None:
    endpoint = f"/public/transactions/{constant.TEST_SOURCE_CHAIN_ID}/{constant.LZ_SOURCE_TX_HASH}"

    response = await test_client.get(endpoint)

    # Assertions
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_transaction_faulty_input_data(
    test_client: AsyncClient,
    transactions_repo: ITransactionsRepo,
    inserted_wormhole_message: None,
) -> None:
    endpoint_faulty_hash = (
        f"/public/transactions/{constant.TEST_SOURCE_CHAIN_ID}/{constant.LZ_SOURCE_TX_HASH}"
        + "1"
    )

    response = await test_client.get(endpoint_faulty_hash)

    # Assertions
    assert response.status_code == 422

    endpoint_faulty_chain_id = (
        f"/public/transactions/1000/{constant.LZ_SOURCE_TX_HASH}" + "1"
    )

    response = await test_client.get(endpoint_faulty_chain_id)

    # Assertions
    assert response.status_code == 422
