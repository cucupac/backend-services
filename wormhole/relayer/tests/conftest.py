import os

import pytest_asyncio
import respx
from databases import Database
from fastapi import FastAPI
from httpx import AsyncClient

import tests.constants as constant
from app.dependencies import get_relays_repo
from app.infrastructure.db.repos.relays import RelaysRepo
from app.infrastructure.web.setup import setup_app
from app.usecases.interfaces.clients.http.evm import IEvmClient
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.interfaces.services.vaa_delivery import IVaaDelivery
from app.usecases.schemas.relays import Status, UpdateRepoAdapter
from app.usecases.services.vaa_delivery import VaaDelivery

# Mocks
from tests.mocks.clients.http.evm import EvmResult, MockEvmClient


# Database Connection
@pytest_asyncio.fixture
async def test_db_url():
    return "postgres://{username}:{password}@{host}:{port}/{database_name}".format(
        username=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5444"),
        database_name=os.getenv("POSTGRES_DB", "ax_relayer_dev_test"),
    )


# RabbitMQ Connection
@pytest_asyncio.fixture
async def test_rmq_url():
    return "amqp://{username}:{password}@{host}:{port}".format(
        username=os.getenv("RMQ_USERNAME", "guest"),
        password=os.getenv("RMQ_PASSWORD", "guest"),
        host=os.getenv("RMQ_HOST", "localhost"),
        port=os.getenv("RMQ_PORT", "5673"),
    )


@pytest_asyncio.fixture
async def test_db(test_db_url) -> Database:
    test_db = Database(url=test_db_url, min_size=5)

    await test_db.connect()
    yield test_db
    await test_db.execute("TRUNCATE transactions CASCADE")
    await test_db.execute("TRUNCATE relays CASCADE")
    await test_db.disconnect()


@pytest_asyncio.fixture
async def relays_repo(test_db: Database) -> IRelaysRepo:
    return RelaysRepo(db=test_db)


@pytest_asyncio.fixture
async def test_evm_client_success() -> IEvmClient:
    return MockEvmClient(result=EvmResult.SUCCESS)


@pytest_asyncio.fixture
async def test_evm_client_fail() -> IEvmClient:
    return MockEvmClient(result=EvmResult.FAILURE)


# Services
@pytest_asyncio.fixture
async def vaa_delivery(
    test_evm_client_success: IEvmClient, relays_repo: IRelaysRepo
) -> IVaaDelivery:
    return VaaDelivery(relays_repo=relays_repo, evm_client=test_evm_client_success)


@pytest_asyncio.fixture
async def vaa_delivery_fail(
    test_evm_client_fail: IEvmClient, relays_repo: IRelaysRepo
) -> IVaaDelivery:
    return VaaDelivery(relays_repo=relays_repo, evm_client=test_evm_client_fail)


# Database-inserted Objects
@pytest_asyncio.fixture
async def inserted_transaction(test_db: Database) -> None:
    async with test_db.transaction():
        transaction_id = await test_db.execute(
            """INSERT INTO transactions (emitter_address, from_address, to_address, source_chain_id, dest_chain_id, amount, sequence) VALUES (:emitter_address, :from_address, :to_address, :source_chain_id, :dest_chain_id, :amount, :sequence) RETURNING id""",
            {
                "emitter_address": constant.TEST_EMITTER_ADDRESS,
                "from_address": constant.TEST_USER_ADDRESS,
                "to_address": constant.TEST_USER_ADDRESS,
                "source_chain_id": constant.TEST_SOURCE_CHAIN_ID,
                "dest_chain_id": constant.TEST_DESTINATION_CHAIN_ID,
                "amount": constant.TEST_AMOUNT,
                "sequence": constant.TEST_SEQUENCE,
            },
        )
        await test_db.execute(
            """INSERT INTO relays (transaction_id, message, status, transaction_hash, error) VALUES (:transaction_id, :message, :status, :transaction_hash, :error)""",
            {
                "transaction_id": transaction_id,
                "status": Status.PENDING,
                "error": None,
                "message": constant.TEST_VAA,
                "transaction_hash": None,
            },
        )


# Repo Adapters
@pytest_asyncio.fixture
async def update_relays_repo_adapter() -> UpdateRepoAdapter:
    return UpdateRepoAdapter(
        emitter_address=constant.TEST_EMITTER_ADDRESS,
        source_chain_id=constant.TEST_SOURCE_CHAIN_ID,
        sequence=constant.TEST_SEQUENCE,
        transaction_hash=constant.TEST_TRANSACTION_HASH,
        error=None,
        status=Status.SUCCESS,
    )


@pytest_asyncio.fixture
def test_app(
    relays_repo: IRelaysRepo,
) -> FastAPI:
    app = setup_app()
    app.dependency_overrides[get_relays_repo] = lambda: relays_repo
    return app


@pytest_asyncio.fixture
async def test_client(test_app: FastAPI) -> AsyncClient:
    respx.route(host="test").pass_through()
    return AsyncClient(app=test_app, base_url="http://test")
