from app.settings import settings
from app.usecases.schemas.blockchain import Chains

CHAIN_DATA = {
    Chains.ETHEREUM.value: {
        "name": "Ethereum",
        "rpc": settings.ethereum_rpc,
        "native": "ETH",
        "post_london_upgrade": True,
        "has_fee_history": True,
    },
    Chains.BSC.value: {
        "name": "BNB Smart Chain",
        "rpc": settings.bsc_rpc,
        "native": "BNB",
        "post_london_upgrade": False,
        "has_fee_history": True,
    },
    Chains.POLYGON.value: {
        "name": "Polygon",
        "rpc": settings.polygon_rpc,
        "native": "MATIC",
        "post_london_upgrade": True,
        "has_fee_history": True,
    },
    Chains.AVALANCHE.value: {
        "name": "Avalanche C-Chain",
        "rpc": settings.avalanche_rpc,
        "native": "AVAX",
        "post_london_upgrade": True,
        "has_fee_history": True,
    },
    Chains.FANTOM.value: {
        "name": "Fantom Opera",
        "rpc": settings.fantom_rpc,
        "native": "FTM",
        "post_london_upgrade": True,
        "has_fee_history": True,
    },
    Chains.ARBITRUM.value: {
        "name": "Arbitrum One",
        "rpc": settings.arbitrum_rpc,
        "native": "ETH",
        "post_london_upgrade": True,
        "has_fee_history": True,
    },
    Chains.CELO.value: {
        "name": "Celo",
        "rpc": settings.celo_rpc,
        "native": "CELO",
        "post_london_upgrade": True,
        "has_fee_history": False,
    },
}
