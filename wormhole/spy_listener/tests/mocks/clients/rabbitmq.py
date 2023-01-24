from app.usecases.interfaces.clients.queues.queue import IQueueClient
from app.usecases.schemas.queue import QueueMessage


class MockRabbitmqClient(IQueueClient):
    def publish(self, message: QueueMessage) -> None:
        """Publishes message to RabbitMQ."""
        return
