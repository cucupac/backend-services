from app.usecases.schemas.blockchain import Chains

CHAIN_ID_LOOKUP = {
    2: Chains.ETHEREUM.value,
    4: Chains.BSC.value,
    5: Chains.POLYGON.value,
    6: Chains.AVALANCHE.value,
    10: Chains.FANTOM.value,
    23: Chains.ARBITRUM.value,
    14: Chains.CELO.value,
    24: Chains.OPTIMISM.value,
}
