from app.settings import settings
from app.usecases.schemas.blockchain import Chains

CHAIN_DATA = {
    Chains.ETHEREUM.value: {
        "name": "Ethereum",
        "rpc": settings.ethereum_rpc,
        "native": "ETH",
        "post_london_upgrade": True,
        "coingecko_id": "ethereum",
    },
    Chains.BSC.value: {
        "name": "BNB Smart Chain",
        "rpc": settings.bsc_rpc,
        "native": "BNB",
        "post_london_upgrade": False,
        "coingecko_id": "binancecoin",
    },
    Chains.POLYGON.value: {
        "name": "Polygon",
        "rpc": settings.polygon_rpc,
        "native": "MATIC",
        "post_london_upgrade": True,
        "coingecko_id": "matic-network",
    },
    Chains.AVALANCHE.value: {
        "name": "Avalanche C-Chain",
        "rpc": settings.avalanche_rpc,
        "native": "AVAX",
        "post_london_upgrade": True,
        "coingecko_id": "avalanche-2",
    },
    Chains.FANTOM.value: {
        "name": "Fantom Opera",
        "rpc": settings.fantom_rpc,
        "native": "FTM",
        "post_london_upgrade": True,
        "coingecko_id": "fantom",
    },
    Chains.ARBITRUM.value: {
        "name": "Arbitrum One",
        "rpc": settings.arbitrum_rpc,
        "native": "ETH",
        "post_london_upgrade": True,
        "coingecko_id": "ethereum",
    },
    Chains.CELO.value: {
        "name": "Celo",
        "rpc": settings.celo_rpc,
        "native": "CELO",
        "post_london_upgrade": True,
        "coingecko_id": "celo",
    },
}
