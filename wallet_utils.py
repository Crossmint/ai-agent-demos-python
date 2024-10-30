import requests
from datetime import datetime

def create_wallet(api_key: str, wallet_type: str, signer_address: str):
    """
    Create a new wallet using Crossmint API
    """
    # Validate wallet type
    valid_wallet_types = ["evm-smart-wallet", "solana-custodial-wallet"]
    if wallet_type not in valid_wallet_types:
        return {
            "error": f"Invalid wallet type. Must be one of: {valid_wallet_types}",
            "timestamp": datetime.utcnow().isoformat()
        }

    endpoint = "{hostname_here}/api/2024-06-09/wallets"
    
    payload = {
        "type": wallet_type,
        "config": {
            "signer": {
                "type": "evm-keypair" if "evm" in wallet_type else "solana-keypair",
                "address": signer_address
            }
        }
    }
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        return {
            "status": "success",
            "wallet_data": response.json(),
            "wallet_type": wallet_type,
            "timestamp": datetime.utcnow().isoformat(),
            "signer_address": signer_address
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }