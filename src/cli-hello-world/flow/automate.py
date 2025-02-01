import os
import sys
from pathlib import Path
import json
import time
from dotenv import load_dotenv

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from library.wallet_utils import (
    create_wallet,
    transfer_usdc,
    get_transaction,
    get_usdc_from_faucet,
    get_wallet_balance
)
load_dotenv()


def automate_wallet_flow():
    try:
        api_key = os.getenv('CROSSMINT_SERVER_API_KEY')
        signer_address = os.getenv('SIGNER_ADDRESS')
        private_key = os.getenv('SIGNER_PRIVATE_KEY')

        # Step 1: Create first wallet
        print("\n1. Creating First EVM Smart Wallet...")
        wallet1_response = create_wallet(api_key, "evm-smart-wallet", signer_address)

        if wallet1_response.get("status") != "success":
            raise Exception(f"First wallet creation failed: {wallet1_response.get('error')}")

        wallet1_address = wallet1_response.get("wallet_data", {}).get("address")
        if not wallet1_address:
            raise Exception("First wallet address not found in response")
        print(f"First wallet created successfully: {wallet1_address}")

        # Step 2: Create second wallet
        print("\n2. Creating Second EVM Smart Wallet...")
        wallet2_response = create_wallet(api_key, "evm-smart-wallet", signer_address)

        if wallet2_response.get("status") != "success":
            raise Exception(f"Second wallet creation failed: {wallet2_response.get('error')}")

        wallet2_address = wallet2_response.get("wallet_data", {}).get("address")
        if not wallet2_address:
            raise Exception("Second wallet address not found in response")
        print(f"Second wallet created successfully: {wallet2_address}")

        # Step 3: Get USDC from faucet for first wallet
        fund_amount = 100
        print(f"\n3. Getting {fund_amount} USDC from faucet for first wallet...")
        faucet_response = get_usdc_from_faucet(api_key, "base-sepolia", wallet1_address, fund_amount)
        if faucet_response.get("status") != "success":
            raise Exception(f"Failed to get USDC from faucet: {faucet_response.get('error')}")

        # Wait and check balance of first wallet
        print("Waiting for faucet transaction to process...")
        time.sleep(5)

        # Step 4: Transfer half of USDC to second wallet
        # Convert to base units (1 USDC = 1,000,000 base units)
        transfer_amount = (fund_amount * 1000000) / 2
        print(f"\n4. Transferring {transfer_amount / 1000000} USDC to second wallet...")
        transaction_response = transfer_usdc(
            api_key,
            wallet1_address,
            wallet2_address,
            int(transfer_amount),  # Convert to integer since we need whole base units
            "base-sepolia",
            private_key
        )

        if transaction_response.get("status") != "success":
            raise Exception(f"Transaction creation failed: {transaction_response.get('error')}")

        transaction_data = transaction_response.get("transaction_data", {})
        transaction_id = transaction_data.get("id")
        if not transaction_id:
            raise Exception("Transaction ID not found in response")

        print(f"Transaction created successfully. ID: {transaction_id}")

        # Wait for transaction to process
        print("\n7. Verifying transaction and final balances...")
        time.sleep(10)

        transaction_status = get_transaction(api_key, wallet1_address, transaction_id)
        if transaction_status.get("status") != "success":
            raise Exception(f"Transaction verification failed: {transaction_status.get('error')}")

        # Check final balances of both wallets
        print("\nChecking final balances...")
        wallet1_final = get_wallet_balance(api_key, "base-sepolia", wallet1_address)
        if wallet1_final.get("status") != "success":
            raise Exception(f"Failed to get wallet1 balance: {wallet1_final.get('error')}")

        wallet2_final = get_wallet_balance(api_key, "base-sepolia", wallet2_address)
        if wallet2_final.get("status") != "success":
            raise Exception(f"Failed to get wallet2 balance: {wallet2_final.get('error')}")

        print(f"\nWallet 1 (was funded with USDC from faucet): {wallet1_address}")
        print(f"Final First Wallet Balance: {wallet1_final.get('balance')} USDC")
        print(f"\nWallet 2 (received USDC from first wallet): {wallet2_address}")
        print(f"Final Second Wallet Balance: {wallet2_final.get('balance')} USDC")

        return {
            "status": "success",
            "message": "Wallet flow completed successfully",
            "data": {
                "wallet1_address": wallet1_address,
                "wallet2_address": wallet2_address,
                "transaction_id": transaction_id,
                "final_status": transaction_status,
                "wallet1_final_balance": wallet1_final.get("balance"),
                "wallet2_final_balance": wallet2_final.get("balance"),
                "explorer_links": {
                    "wallet1": f"https://sepolia.basescan.org/address/{wallet1_address}#tokentxns",
                    "wallet2": f"https://sepolia.basescan.org/address/{wallet2_address}#tokentxns"
                }
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":
    print("Starting automated wallet flow...")
    result = automate_wallet_flow()
    print(f"\nFinal Result: {json.dumps(result, indent=2)}")
