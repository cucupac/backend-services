import tests.constants as constant
from app.usecases.interfaces.clients.bridge import IBridgeClient
from app.usecases.schemas.bridge import BridgeClientException, BridgeMessage


class MockWormholeClient(IBridgeClient):
    def __init__(self) -> None:
        self.called_before = False

    async def fetch_bridge_message(
        self, emitter_address: str, emitter_chain_id: int, sequence: int
    ) -> BridgeMessage:
        if emitter_chain_id == constant.TEST_SOURCE_CHAIN_ID and not self.called_before:
            self.called_before = True
            return BridgeMessage(b64_message=constant.TEST_BASE64_ENCODED_VAA)
        raise BridgeClientException()
