from app.settings import settings
from app.usecases.schemas.blockchain import AxChains

CHAIN_DATA = {
    AxChains.ETHEREUM.value: {
        "name": "Ethereum",
        "chain_id": 1,
        "wh_chain_id": 2,
        "lz_chain_id": 101,
        "rpc": settings.ethereum_rpc,
        "native": "ETH",
        "post_london_upgrade": True,
        "has_fee_history": True,
        "max_block_range": 100_000,
    },
    AxChains.BSC.value: {
        "name": "BNB Smart Chain",
        "chain_id": 56,
        "wh_chain_id": 4,
        "lz_chain_id": 102,
        "rpc": settings.bsc_rpc,
        "native": "BNB",
        "post_london_upgrade": False,
        "has_fee_history": True,
        "max_block_range": 3_000,
    },
    AxChains.POLYGON.value: {
        "name": "Polygon",
        "chain_id": 137,
        "wh_chain_id": 5,
        "lz_chain_id": 109,
        "rpc": settings.polygon_rpc,
        "native": "MATIC",
        "post_london_upgrade": True,
        "has_fee_history": True,
        "max_block_range": 100_000,
    },
    AxChains.AVALANCHE.value: {
        "name": "Avalanche C-Chain",
        "chain_id": 43114,
        "wh_chain_id": 6,
        "lz_chain_id": 106,
        "rpc": settings.avalanche_rpc,
        "native": "AVAX",
        "post_london_upgrade": True,
        "has_fee_history": True,
        "max_block_range": 100_000,
    },
    AxChains.FANTOM.value: {
        "name": "Fantom Opera",
        "chain_id": 250,
        "wh_chain_id": 10,
        "lz_chain_id": 112,
        "rpc": settings.fantom_rpc,
        "native": "FTM",
        "post_london_upgrade": True,
        "has_fee_history": True,
        "max_block_range": 100_000,
    },
    AxChains.ARBITRUM.value: {
        "name": "Arbitrum One",
        "chain_id": 42161,
        "wh_chain_id": 23,
        "lz_chain_id": 110,
        "rpc": settings.arbitrum_rpc,
        "native": "ETH",
        "post_london_upgrade": True,
        "has_fee_history": True,
        "max_block_range": 100_000,
    },
    AxChains.CELO.value: {
        "name": "Celo",
        "chain_id": 42220,
        "wh_chain_id": 14,
        "lz_chain_id": 125,
        "rpc": settings.celo_rpc,
        "native": "CELO",
        "post_london_upgrade": True,
        "has_fee_history": False,
        "max_block_range": 100_000,
    },
    AxChains.GNOSIS.value: {
        "name": "Gnosis",
        "chain_id": 100,
        # "wh_chain_id": 25,
        "lz_chain_id": 145,
        "rpc": settings.gnosis_rpc,
        "native": "xDAI",
        "post_london_upgrade": True,
        "has_fee_history": True,
        "max_block_range": 100_000,
    },
    AxChains.OPTIMISM.value: {
        "name": "Optimism",
        "chain_id": 10,
        # "wh_chain_id": 24,
        "lz_chain_id": 111,
        "rpc": settings.optimism_rpc,
        "native": "ETH",
        "post_london_upgrade": True,
        "has_fee_history": True,
        "max_block_range": 3_000,
    },
}
