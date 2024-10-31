import requests
from datetime import datetime
import os

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

    # Hit the Crossmint Staging API
    endpoint = f"https://staging.crossmint.com/api/v1-alpha2/wallets"
    
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

        if not response.ok:
            error_message = "Unknown error"
            try:
                error_data = response.json()
                error_message = error_data.get('message', str(response.text))
            except:
                error_message = str(response.text)
                
            return {
                "status": "error",
                "error": f"API Error: {error_message}",
                "timestamp": datetime.utcnow().isoformat()
            }
                
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "wallet_data": response.json(),
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }