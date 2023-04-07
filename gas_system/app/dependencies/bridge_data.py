from app.usecases.schemas.blockchain import Chains

BRIDGE_DATA = {
    Chains.ETHEREUM.value: {"wormhole": {"chain_id": 2}},
    Chains.BSC.value: {"wormhole": {"chain_id": 4}},
    Chains.POLYGON.value: {"wormhole": {"chain_id": 5}},
    Chains.AVALANCHE.value: {"wormhole": {"chain_id": 6}},
    Chains.FANTOM.value: {"wormhole": {"chain_id": 10}},
    Chains.ARBITRUM.value: {"wormhole": {"chain_id": 23}},
    Chains.CELO.value: {"wormhole": {"chain_id": 14}},
}
