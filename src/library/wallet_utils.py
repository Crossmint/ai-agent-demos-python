import requests
import os
from datetime import datetime
from web3 import Web3
from eth_abi import encode
from eth_utils import function_signature_to_4byte_selector
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
    endpoint = f"https://staging.crossmint.com/api/2022-06-09/wallets"

    payload = {
        "type": wallet_type,
        "config": {
            "adminSigner": {
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


def get_usdc_from_faucet(api_key: str, chain: str, wallet_address: str, amount: int):
    """
    Get USDC from the Crossmint faucet

    Args:
        api_key (str): Crossmint API key
        chain (str): Blockchain network
        wallet_address (str): Wallet address to fund
        amount (int): Amount of USDC to request

    Returns:
        dict: Response containing status and transaction data or error message
    """
    endpoint = f"https://staging.crossmint.com/api/v1-alpha2/wallets/{
        wallet_address}/balances"

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "amount": amount,
        "chain": chain,
        "currency": "usdxm"
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers)

        if not response.ok:
            error_message = "Unknown error"
            try:
                error_data = response.json()
                if response.status_code == 429 and error_data.get("error") and error_data.get("message"):
                    return {
                        "status": "error",
                        "error": error_data["message"],
                        "timestamp": datetime.utcnow().isoformat()
                    }
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


def transfer_usdc(api_key: str, from_wallet_address: str, to_wallet_address: str, amount: int, chain: str = "base-sepolia", private_key: str = None):
    """
    Transfer USDC from one wallet to another

    Args:
        api_key (str): Crossmint API key
        from_wallet_address (str): Source wallet address
        to_wallet_address (str): Destination wallet address
        amount (int): Amount in USDC base units (1000000 = 1 USDC)
        chain (str): Blockchain network (default: "base-sepolia")
        private_key (str): Private key for signing the transaction
    """
    usdc_contract_address = "0x14196F08a4Fa0B66B7331bC40dd6bCd8A1dEeA9F"

    # Make sure to_wallet_address is checksummed
    to_wallet_address = Web3.to_checksum_address(to_wallet_address)

    # Encode the transfer function call
    transfer_selector = function_signature_to_4byte_selector(
        'transfer(address,uint256)')
    encoded_params = encode(['address', 'uint256'], [
                            to_wallet_address, amount])
    encoded_transfer = transfer_selector + encoded_params

    params = {
        "calls": [{
            "to": usdc_contract_address,
            "value": "0",
            "data": f"0x{encoded_transfer.hex()}"
        }],
        "chain": chain
    }

    # Create the transaction
    tx_response = create_transaction(
        api_key, from_wallet_address, chain, params)

    if tx_response["status"] != "success":
        return tx_response

    tx_data = tx_response["transaction_data"]

    # Check if transaction is awaiting approval
    if tx_data["status"] != "awaiting-approval":
        return {
            "status": "error",
            "error": f"Unexpected transaction status: {tx_data['status']}",
            "transaction_data": tx_data,
            "timestamp": datetime.utcnow().isoformat()
        }

    # If no private key provided, return the transaction data for later signing
    if not private_key:
        return {
            "status": "awaiting_signature",
            "message": "Transaction created but requires signing. Please provide private key.",
            "transaction_data": tx_data,
            "timestamp": datetime.utcnow().isoformat()
        }

    # Get the user operation hash that needs to be signed
    user_op_hash = tx_data["onChain"]["userOperationHash"]

    # Generate signature
    signature = generate_signature(private_key, user_op_hash)

    # Get the signer ID from the pending approval
    signer_id = tx_data["approvals"]["pending"][0]["signer"]

    # Submit the signature
    signature_response = submit_transaction_approval(
        api_key=api_key,
        user_op_sender=from_wallet_address,
        transaction_id=tx_data["id"],
        signer_id=signer_id,
        signature=signature
    )

    return signature_response


def create_transaction(api_key: str, wallet_address: str, chain: str, params: dict = None):
    """
    Create a transaction with specific parameters

    Args:
        api_key (str): Crossmint API key
        wallet_address (str): Source wallet address
        chain (str): Blockchain network
        params (dict): Transaction parameters containing calls and other configuration

    Returns:
        dict: Response containing status and transaction data in the format:
        {
            "status": "success",
            "transaction_data": {
                "id": str,
                "walletType": str,
                "status": str,
                "approvals": {
                    "pending": [{"signer": str, "message": str}],
                    "submitted": []
                },
                "params": dict,
                "onChain": dict,
                "createdAt": str
            }
        }
    """

    endpoint = f"https://staging.crossmint.com/api/2022-06-09/wallets/{
        wallet_address}/transactions"

    # Use provided params or default to a basic transaction
    default_params = {
        "calls": [
            {
                "to": "0x5c030a01e9d2c4bb78212d06f88b7724b494b755",
                "value": "0",
                "data": "0x"
            }
        ],
        "chain": chain
    }

    payload = {
        "params": params or default_params
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

        # Return the response data directly as transaction_data
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

    Args:
        private_key (str): The private key to sign with
        user_op_hash (str): The user operation hash to sign

    Returns:
        str: The generated signature with '0x' prefix

    Raises:
        ValueError: If private_key or user_op_hash is None, empty, or not a valid hex string
    """
    if not private_key:
        raise ValueError("Private key is required")

    if not user_op_hash:
        raise ValueError("User operation hash is required")

    # Validate user_op_hash is a valid hex string
    try:
        if not user_op_hash.startswith('0x'):
            raise ValueError("User operation hash must start with '0x'")
        # Try to convert to bytes to validate it's a proper hex string
        bytes.fromhex(user_op_hash.replace('0x', ''))
    except (ValueError, AttributeError):
        raise ValueError("Invalid user operation hash format")

    try:
        w3 = Web3()
        account = w3.eth.account.from_key(private_key)
    except (ValueError, AttributeError):
        raise ValueError("Invalid private key format")

    # Convert the hash to bytes and sign it as an Ethereum message
    message_bytes = bytes.fromhex(user_op_hash.replace('0x', ''))
    eth_message = encode_defunct(primitive=message_bytes)
    signed_message = account.sign_message(eth_message)

    # Add '0x' prefix to the signature
    return '0x' + signed_message.signature.hex()


def submit_transaction_approval(
    api_key: str,
    user_op_sender: str,
    transaction_id: str,
    signer_id: str,
    signature: str
) -> dict:
    """
    Submit an approval for a transaction

    Args:
        api_key (str): Crossmint API key
        user_op_sender (str): The wallet address that created the transaction
        transaction_id (str): The transaction ID to approve
        signer_id (str): The ID of the signer (e.g. "0x123...")
        signature (str): The signature for the transaction

    Returns:
        dict: Response containing status and transaction data or error in the format:
        {
            "status": "success",
            "transaction_data": {
                "id": str,
                "walletType": str,
                "status": str,
                "approvals": {
                    "pending": [],
                    "submitted": [{"signer": str, "signature": str}]
                },
                "params": dict,
                "onChain": dict,
                "createdAt": str
            }
        }
    """
    endpoint = f"https://staging.crossmint.com/api/2022-06-09/wallets/{user_op_sender}/transactions/{transaction_id}/approvals"

    payload = {
        "approvals": [
            {
                "signer": signer_id,
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
    endpoint = f"https://staging.crossmint.com/api/2022-06-09/wallets/{
        user_op_sender}/transactions/{transaction_id}"

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


def get_wallet_balance(api_key: str, chain: str, wallet_address: str):
    """
    Get the balance of a wallet using Crossmint API
    """

    # Hit the Crossmint Staging API
    endpoint = f"https://staging.crossmint.com/api/unstable/wallets/{
        chain}:{wallet_address}/tokens"

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
        # Find USDC token balance from response array
        usdc_token = next((token for token in response_json if token.get(
            "tokenMetadata", {}).get("symbol") == "USDC"), None)
        balance = "0x0"
        if usdc_token:
            balance = usdc_token.get("tokenBalance", "0x0")
        human_readable_balance = int(balance, 16) / 10**6

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
