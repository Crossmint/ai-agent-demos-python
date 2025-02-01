def tools_schema():
    return [
        {
            "type": "function",
            "function": {
                "name": "create_new_wallet",
                "description": "Creates a new blockchain wallet",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "wallet_type": {
                            "type": "string",
                            "enum": ["evm-smart-wallet", "solana-custodial-wallet"],
                            "description": "The type of wallet to create"
                        },
                    },
                    "required": ["wallet_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_wallet_balance",
                "description": "Get the balance of a wallet",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "wallet_address": {
                            "type": "string",
                            "description": "The address of the wallet"
                        }
                    },
                    "required": ["wallet_address"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_transaction",
                "description": "Create and submit a new transaction for a selected wallet",
                "parameters": {
                    "type": "object",
                    "properties": {},  # No parameters needed as wallet selection is handled internally
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_usdc_from_faucet",
                "description": "Get USDC tokens from the faucet for a specified wallet",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "wallet_address": {
                            "type": "string",
                            "description": "The address of the wallet to receive USDC"
                        },
                        "amount": {
                            "type": "integer",
                            "description": "Amount of USDC to request (in whole units)"
                        }
                    },
                    "required": ["wallet_address", "amount"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "transfer_usdc",
                "description": "Transfer USDC from one wallet to another",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "from_wallet_address": {
                            "type": "string",
                            "description": "The source wallet address"
                        },
                        "to_wallet_address": {
                            "type": "string",
                            "description": "The destination wallet address"
                        },
                        "amount": {
                            "type": "integer",
                            "description": "Amount of USDC to transfer (in whole units)"
                        }
                    },
                    "required": ["from_wallet_address", "to_wallet_address", "amount"]
                }
            }
        }
    ]
