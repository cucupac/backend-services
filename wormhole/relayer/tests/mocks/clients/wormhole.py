import tests.constants as constant
from app.usecases.interfaces.clients.bridge import IBridgeClient
from app.usecases.schemas.bridge import BridgeClientException, BridgeMessage


class MockWormholeClient(IBridgeClient):
    async def fetch_bridge_message(
        self, emitter_address: str, emitter_chain_id: int, sequence: int
    ) -> BridgeMessage:
        try:
            vaa_bytes = constant.MISSING_VAAS[emitter_chain_id][sequence]["vaa_bytes"]
            return BridgeMessage(b64_message=vaa_bytes)
        except:
            raise BridgeClientException()
