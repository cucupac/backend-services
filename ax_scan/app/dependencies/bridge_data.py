from app.settings import settings
from app.usecases.schemas.blockchain import AxChains

WH_LOOKUP = {
    2: AxChains.ETHEREUM.value,
    4: AxChains.BSC.value,
    5: AxChains.POLYGON.value,
    6: AxChains.AVALANCHE.value,
    10: AxChains.FANTOM.value,
    23: AxChains.ARBITRUM.value,
    14: AxChains.CELO.value,
    24: AxChains.OPTIMISM.value,
}

LZ_LOOKUP = {
    101: AxChains.ETHEREUM.value,
    102: AxChains.BSC.value,
    109: AxChains.POLYGON.value,
    106: AxChains.AVALANCHE.value,
    112: AxChains.FANTOM.value,
    110: AxChains.ARBITRUM.value,
    125: AxChains.CELO.value,
    111: AxChains.OPTIMISM.value,
    145: AxChains.GNOSIS.value,
}

BRIDGE_DATA = {
    AxChains.ETHEREUM.value: {
        "wormhole": {"chain_id": 2, "emitter_address": settings.evm_wormhole_bridge},
        "layer_zero": {
            "chain_id": 101,
            "emitter_address": settings.evm_layerzero_bridge,
        },
    },
    AxChains.BSC.value: {
        "wormhole": {"chain_id": 4, "emitter_address": settings.evm_wormhole_bridge},
        "layer_zero": {
            "chain_id": 102,
            "emitter_address": settings.evm_layerzero_bridge,
        },
    },
    AxChains.POLYGON.value: {
        "wormhole": {"chain_id": 5, "emitter_address": settings.evm_wormhole_bridge},
        "layer_zero": {
            "chain_id": 109,
            "emitter_address": settings.evm_layerzero_bridge,
        },
    },
    AxChains.AVALANCHE.value: {
        "wormhole": {"chain_id": 6, "emitter_address": settings.evm_wormhole_bridge},
        "layer_zero": {
            "chain_id": 106,
            "emitter_address": settings.evm_layerzero_bridge,
        },
    },
    AxChains.FANTOM.value: {
        "wormhole": {"chain_id": 10, "emitter_address": settings.evm_wormhole_bridge},
        "layer_zero": {
            "chain_id": 112,
            "emitter_address": settings.evm_layerzero_bridge,
        },
    },
    AxChains.ARBITRUM.value: {
        "wormhole": {"chain_id": 23, "emitter_address": settings.evm_wormhole_bridge},
        "layer_zero": {
            "chain_id": 110,
            "emitter_address": settings.evm_layerzero_bridge,
        },
    },
    AxChains.CELO.value: {
        "wormhole": {"chain_id": 14, "emitter_address": settings.evm_wormhole_bridge},
        "layer_zero": {
            "chain_id": 125,
            "emitter_address": settings.evm_layerzero_bridge,
        },
    },
    AxChains.OPTIMISM.value: {
        "wormhole": {"chain_id": 24, "emitter_address": settings.evm_wormhole_bridge},
        "layer_zero": {
            "chain_id": 111,
            "emitter_address": settings.evm_layerzero_bridge,
        },
    },
    AxChains.GNOSIS.value: {
        "layer_zero": {
            "chain_id": 145,
            "emitter_address": settings.evm_layerzero_bridge,
        }
    },
}
