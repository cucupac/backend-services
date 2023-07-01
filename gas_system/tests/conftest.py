# pylint: disable=redefined-outer-name
import os

import pytest_asyncio
import respx
from databases import Database
from fastapi import FastAPI
from httpx import AsyncClient

import tests.constants as constant
from app.dependencies import CHAIN_DATA
from app.infrastructure.db.repos.fee_updates import FeeUpdatesRepo
from app.infrastructure.db.repos.transactions import TransactionsRepo
from app.infrastructure.web.setup import setup_app
from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.interfaces.clients.http.prices import IPriceClient
from app.usecases.interfaces.repos.fee_updates import IFeeUpdatesRepo
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.interfaces.services.remote_price_manager import IRemotePriceManager
from app.usecases.schemas.fees import FeeUpdate
from app.usecases.schemas.transactions import CacheStatus, GrpcStatus, Status
from app.usecases.services.remote_price_manager import RemotePriceManager
from tests.mocks.clients.http.coingecko import MockPriceClient

# Mocks
from tests.mocks.clients.http.evm_wormhole_bridge import (
    EvmResult,
    MockWormholeBridgeEvmClient,
)


# Database Connection
@pytest_asyncio.fixture
async def test_db_url():
    username = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5444")
    database_name = os.getenv("POSTGRES_DB", "ax_relayer_dev_test")
    return f"postgres://{username}:{password}@{host}:{port}/{database_name}"


@pytest_asyncio.fixture
async def test_db(test_db_url) -> Database:
    test_db = Database(url=test_db_url, min_size=5)

    await test_db.connect()
    yield test_db
    await test_db.execute("TRUNCATE transactions CASCADE")
    await test_db.execute("TRUNCATE relays CASCADE")
    await test_db.execute("TRUNCATE fee_updates CASCADE")
    await test_db.disconnect()


# Repos (Database Gateways)
@pytest_asyncio.fixture
async def transactions_repo(test_db: Database) -> ITransactionsRepo:
    return TransactionsRepo(db=test_db)


@pytest_asyncio.fixture
async def fee_updates_repo(test_db: Database) -> IFeeUpdatesRepo:
    return FeeUpdatesRepo(db=test_db)


# Clients
@pytest_asyncio.fixture
async def test_evm_clients_success() -> IBlockchainClient:
    supported_evm_clients = {}
    for chain_id in CHAIN_DATA:
        supported_evm_clients[chain_id] = MockWormholeBridgeEvmClient(
            result=EvmResult.SUCCESS, chain_id=chain_id
        )
    return supported_evm_clients


@pytest_asyncio.fixture
async def test_evm_clients_failure() -> IBlockchainClient:
    supported_evm_clients = {}
    for chain_id in CHAIN_DATA:
        supported_evm_clients[chain_id] = MockWormholeBridgeEvmClient(
            result=EvmResult.FAILURE, chain_id=chain_id
        )
    return supported_evm_clients


@pytest_asyncio.fixture
async def test_price_client() -> IPriceClient:
    return MockPriceClient()


# Services
@pytest_asyncio.fixture
async def remote_price_manager(
    test_evm_clients_success: IBlockchainClient,
    fee_updates_repo: IFeeUpdatesRepo,
    test_price_client: IPriceClient,
) -> IRemotePriceManager:
    return RemotePriceManager(
        price_client=test_price_client,
        blockchain_clients=test_evm_clients_success,
        fee_update_repo=fee_updates_repo,
    )


@pytest_asyncio.fixture
async def remote_price_manager_failed(
    test_evm_clients_failure: IBlockchainClient,
    fee_updates_repo: IFeeUpdatesRepo,
    test_price_client: IPriceClient,
) -> IRemotePriceManager:
    return RemotePriceManager(
        price_client=test_price_client,
        blockchain_clients=test_evm_clients_failure,
        fee_update_repo=fee_updates_repo,
    )


@pytest_asyncio.fixture
async def test_fee_update() -> FeeUpdate:
    return FeeUpdate(
        chain_id=constant.TEST_CHAIN_ID,
        updates=constant.TEST_UPDATE,
        transaction_hash=constant.TEST_TRANSACTION_HASH,
        status=Status.SUCCESS,
        error=None,
    )


# Database-inserted Objects
@pytest_asyncio.fixture
async def testing_transaction(test_db: Database) -> None:
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
            """INSERT INTO relays (transaction_id, message, status, transaction_hash, error, cache_status, grpc_status) VALUES (:transaction_id, :message, :status, :transaction_hash, :error, :cache_status, :grpc_status)""",
            {
                "transaction_id": transaction_id,
                "status": Status.TESTING,
                "error": None,
                "message": constant.TEST_VAA,
                "transaction_hash": None,
                "cache_status": CacheStatus.NEVER_CACHED,
                "grpc_status": GrpcStatus.FAILED,
            },
        )


@pytest_asyncio.fixture
def test_app(
    # example_repo: IExampleRepo,
) -> FastAPI:
    app = setup_app()
    # app.dependency_overrides[get_example_repo] = lambda: example_repo
    return app


@pytest_asyncio.fixture
async def test_client(test_app: FastAPI) -> AsyncClient:
    respx.route(host="test").pass_through()
    return AsyncClient(app=test_app, base_url="http://test")
