import pytest
from aio_pika import RobustConnection

from app.dependencies import get_connection, get_rmq_client
from app.infrastructure.clients.queues.rabbitmq import RabbitmqClient


@pytest.mark.asyncio
async def test_get_rmq_client() -> None:
    """Tests that queue connection is successfully established."""

    test_queue_client = await get_rmq_client()
    test_connection = await get_connection()

    assert type(test_queue_client) == RabbitmqClient
    assert type(test_connection) == RobustConnection
