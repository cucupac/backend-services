ABI = [
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "address",
                "name": "previousAdmin",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "address",
                "name": "newAdmin",
                "type": "address",
            },
        ],
        "name": "AdminChanged",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "beacon",
                "type": "address",
            }
        ],
        "name": "BeaconUpgraded",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "uint8",
                "name": "version",
                "type": "uint8",
            }
        ],
        "name": "Initialized",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "previousOwner",
                "type": "address",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "newOwner",
                "type": "address",
            },
        ],
        "name": "OwnershipTransferred",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "_srcChainId",
                "type": "uint16",
            },
            {
                "indexed": True,
                "internalType": "bytes",
                "name": "_srcAddress",
                "type": "bytes",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "_toAddress",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "_amount",
                "type": "uint256",
            },
        ],
        "name": "ReceiveFromChain",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint16",
                "name": "_dstChainId",
                "type": "uint16",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "_from",
                "type": "address",
            },
            {
                "indexed": True,
                "internalType": "bytes",
                "name": "_toAddress",
                "type": "bytes",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "_amount",
                "type": "uint256",
            },
        ],
        "name": "SendToChain",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "implementation",
                "type": "address",
            }
        ],
        "name": "Upgraded",
        "type": "event",
    },
    {
        "inputs": [{"internalType": "address", "name": "_token", "type": "address"}],
        "name": "extractERC20",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "extractNative",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "feeSetter",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getTrustedContracts",
        "outputs": [{"internalType": "bytes32[]", "name": "", "type": "bytes32[]"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getTrustedRelayers",
        "outputs": [{"internalType": "address[]", "name": "", "type": "address[]"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_wormholeCoreBridge",
                "type": "address",
            },
            {"internalType": "address", "name": "_usx", "type": "address"},
        ],
        "name": "initialize",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "_contract", "type": "bytes32"},
            {"internalType": "bool", "name": "_isTrusted", "type": "bool"},
        ],
        "name": "manageTrustedContracts",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "_relayer", "type": "address"},
            {"internalType": "bool", "name": "_isTrusted", "type": "bool"},
        ],
        "name": "manageTrustedRelayers",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes", "name": "_vaa", "type": "bytes"}],
        "name": "processMessage",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "name": "processedMessages",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "proxiableUUID",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "renounceOwnership",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint16", "name": "", "type": "uint16"}],
        "name": "sendFeeLookup",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address payable", "name": "_from", "type": "address"},
            {"internalType": "uint16", "name": "_dstChainId", "type": "uint16"},
            {"internalType": "bytes", "name": "_toAddress", "type": "bytes"},
            {"internalType": "uint256", "name": "_amount", "type": "uint256"},
        ],
        "name": "sendMessage",
        "outputs": [{"internalType": "uint64", "name": "sequence", "type": "uint64"}],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "_feeSetter", "type": "address"}
        ],
        "name": "setFeeSetter",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint16[]", "name": "_destChainIds", "type": "uint16[]"},
            {"internalType": "uint256[]", "name": "_fees", "type": "uint256[]"},
        ],
        "name": "setSendFees",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "newOwner", "type": "address"}],
        "name": "transferOwnership",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "name": "trustedContracts",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "name": "trustedRelayers",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "newImplementation", "type": "address"}
        ],
        "name": "upgradeTo",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "newImplementation", "type": "address"},
            {"internalType": "bytes", "name": "data", "type": "bytes"},
        ],
        "name": "upgradeToAndCall",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "usx",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "wormholeCoreBridge",
        "outputs": [
            {"internalType": "contract IWormhole", "name": "", "type": "address"}
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {"stateMutability": "payable", "type": "receive"},
]
