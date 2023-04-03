from app.settings import settings
from app.usecases.schemas.blockchain import Chains

CHAIN_DATA = {
    Chains.ETHEREUM.value: {
        "rpc": settings.ethereum_rpc,
        "native": "ETH",
    },
    Chains.BSC.value: {
        "rpc": settings.bsc_rpc,
        "native": "BNB",
    },
    Chains.POLYGON.value: {
        "rpc": settings.polygon_rpc,
        "native": "MATIC",
    },
    Chains.AVALANCHE.value: {
        "rpc": settings.avalanche_rpc,
        "native": "AVAX",
    },
    Chains.FANTOM.value: {
        "rpc": settings.fantom_rpc,
        "native": "FTM",
    },
    Chains.ARBITRUM.value: {
        "rpc": settings.arbitrum_rpc,
        "native": "ETH",
    },
    Chains.CELO.value: {
        "rpc": settings.celo_rpc,
        "native": "CELO",
    },
}
