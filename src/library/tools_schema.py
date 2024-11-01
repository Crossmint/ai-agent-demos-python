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
                "name": "deposit_tokens",
                "description": "Deposit tokens from treasury to a wallet",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "wallet_address": {
                            "type": "string",
                            "description": "The address of the wallet to deposit to"
                        },
                        "amount": {
                            "type": "number",
                            "description": "Amount of tokens to deposit"
                        }
                    },
                    "required": ["wallet_address", "amount"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "transfer_tokens_to_wallet",
                "description": "Transfer tokens between wallets (you will be prompted to select the destination wallet)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "chain": {
                            "type": "string",
                            "enum": ["ethereum-sepolia", "solana-devnet"],
                            "description": "The chain to transfer on (for now only sepolia and devnet are supported)"
                        },
                        "amount": {
                            "type": "number",
                            "description": "Amount of tokens to transfer"
                        }
                    },
                    "required": ["chain", "amount"]
                }
            }
        }
    ]