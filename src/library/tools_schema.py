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
        }
    ]