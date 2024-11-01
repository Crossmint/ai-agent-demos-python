import requests
import os
from datetime import datetime
from web3 import Web3

from eth_account.messages import encode_defunct

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

def create_transaction(api_key: str, wallet_address: str, chain: str):
    """
    Create a transaction with specific parameters
    
    Args:
        api_key (str): Crossmint API key
        wallet_address (str): Source wallet address
        to_address (str): Destination contract/wallet address
    """
    
    endpoint = f"https://staging.crossmint.com/api/v1-alpha2/wallets/{wallet_address}/transactions/{chain}"
    
    payload = {
        "params": {
            "calls": [
                {
                    "to": "0x5c030a01e9d2c4bb78212d06f88b7724b494b755",
                    "value": "0",
                    "data": "0x"
                }
            ]
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
            "transaction_data": response.json()
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
    
def generate_signature(private_key: str, user_op_hash: str) -> str:
    """
    Generate a signature for a user operation hash using a private key
    """
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)
    
    # Convert the hash to bytes and sign it as an Ethereum message
    message_bytes = bytes.fromhex(user_op_hash.replace('0x', ''))
    eth_message = encode_defunct(primitive=message_bytes)
    signed_message = account.sign_message(eth_message)
    
    return signed_message.signature.hex()


def submit_transaction_signature(
    api_key: str,
    user_op_sender: str, 
    transaction_id: str, 
    signer_id: str,
    signature: str
) -> dict:
    """
    Submit signature for a transaction
    
    Args:
        api_key (str): Crossmint API key
        user_op_sender (str): The user op sender
        transaction_id (str): The transaction ID
        signer_id (str): The signer ID
        signature (str): The signature
            
    Returns:
        dict: Response containing status and transaction data or error
    """
    endpoint = f"https://staging.crossmint.com/api/v1-alpha2/wallets/{user_op_sender}/transactions/base-sepolia/{transaction_id}/signatures"
    
    payload = {
        "signatures": [
            {
                "signerId": signer_id,
                "signature": signature
            }
        ]
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
            "transaction_data": response.json()
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
    
def get_transaction(api_key: str, user_op_sender: str, transaction_id: str) -> dict:
    """
    Get a transaction response
    
    Args:
        api_key (str): Crossmint API key
        user_op_sender (str): The wallet address
        transaction_id (str): The transaction ID
    
    Returns:
        dict: Transaction response or error message
    """
    endpoint = f"https://staging.crossmint.com/api/v1-alpha2/wallets/{user_op_sender}/transactions/base-sepolia/{transaction_id}"
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(endpoint, headers=headers)
        
        if response.ok:
            return {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "transaction_data": response.json()
            }
        else:
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
            
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
    
def get_wallet_balance(api_key: str, chain:str, wallet_address: str):
    """
    Get the balance of a wallet using Crossmint API
    """

    # Hit the Crossmint Staging API
    endpoint = f"https://staging.crossmint.com/api/unstable/wallets/{chain}:{wallet_address}/tokens"

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(endpoint, headers=headers)
        
        if not response.ok:
            return {
                "status": "error",
                "error": f"API Error: {response.text}",
                "timestamp": datetime.utcnow().isoformat()
            }

        response_json = response.json()
        # Get token balance in hex format and convert to decimal
        balance = response_json[0]['tokenBalance']
        human_readable_balance = int(balance, 16) / 10**18

        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "balance": human_readable_balance,
        }

    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

def deposit_tokens(api_key: str, treasury_wallet: str, destination_wallet: str, amount: float):
    """
    Deposit tokens from treasury wallet to a user wallet
    
    Args:
        api_key (str): Crossmint API key
        treasury_wallet (str): Wallet address to send tokens from (must be funded beforehand)
        destination_wallet (str): Wallet address to receive tokens
        amount (float): Amount in ETH to transfer
    """

    # TODO: Make this dynamic
    CHAIN = "ethereum-sepolia"
    
    # Convert amount to wei (multiply by 10**18)
    amount_in_wei = hex(int(amount * 10**18))
    
    endpoint = f"https://staging.crossmint.com/api/v1-alpha2/wallets/{treasury_wallet}/transactions/{CHAIN}"
    
    payload = {
        "to": destination_wallet,
        "value": amount_in_wei,
        "data": "0x"
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
            "transaction_data": response.json()
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

def transfer_tokens(api_key: str, from_wallet: str, to_wallet: str, amount: float):
    """
    Transfer tokens from one wallet to another
    
    Args:
        api_key (str): Crossmint API key
        from_wallet (str): Source wallet address
        to_wallet (str): Destination wallet address
        amount (float): Amount in ETH to transfer
    """
    CHAIN = "ethereum-sepolia"
    
    # Convert amount to wei (multiply by 10**18)
    amount_in_wei = hex(int(amount * 10**18))
    
    endpoint = f"https://staging.crossmint.com/api/v1-alpha2/wallets/{from_wallet}/transactions/{CHAIN}"
    
    payload = {
        "to": to_wallet,
        "value": amount_in_wei,
        "data": "0x"
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
            "transaction_data": response.json()
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }