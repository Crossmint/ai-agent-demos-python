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
    generate_signature,
    submit_transaction_signature,
    get_transaction,
    get_usdc_from_faucet,
    get_wallet_balance
)

load_dotenv()

def automate_wallet_flow():
    try:
        api_key = os.getenv('CROSSMINT_SERVER_API_KEY')
        signer_address = os.getenv('SIGNER_ADDRESS')

        # Step 1: Create first wallet
        print("\n1. Creating First EVM Smart Wallet...")
        wallet1_response = create_wallet(api_key, "evm-smart-wallet", signer_address)
        
        if wallet1_response.get("status") != "success":
            raise Exception("First wallet creation failed")
        
        wallet1_address = wallet1_response.get("wallet_data", {}).get("address")
        print(f"First wallet created successfully: {wallet1_address}")

        # Step 2: Create second wallet
        print("\n2. Creating Second EVM Smart Wallet...")
        wallet2_response = create_wallet(api_key, "evm-smart-wallet", signer_address)
        
        if wallet2_response.get("status") != "success":
            raise Exception("Second wallet creation failed")
        
        wallet2_address = wallet2_response.get("wallet_data", {}).get("address")
        print(f"Second wallet created successfully: {wallet2_address}")

        # Step 3: Get USDC from faucet for first wallet
        fund_amount = 100
        print(f"\n3. Getting {fund_amount} USDC from faucet for first wallet...")
        faucet_response = get_usdc_from_faucet("base-sepolia", wallet1_address, fund_amount)
        if faucet_response.get("status") != "success":
            raise Exception("Failed to get USDC from faucet")
        
        # Wait and check balance of first wallet
        print("Waiting for faucet transaction to process...")
        time.sleep(5)

        # Step 4: Transfer half of USDC to second wallet
        transfer_amount = (fund_amount * 1000000) / 2  # Convert to base units (1 USDC = 1,000,000 base units)
        print(f"\n4. Transferring {transfer_amount/1000000} USDC to second wallet...")
        transaction_response = transfer_usdc(
            api_key, 
            wallet1_address, 
            wallet2_address, 
            int(transfer_amount),  # Convert to integer since we need whole base units
            "base-sepolia"
        )
        
        if transaction_response.get("status") != "success":
            raise Exception("Transaction creation failed")
            
        transaction_data = transaction_response.get("transaction_data", {})
        transaction_id = transaction_data.get("id")
        user_op_hash = transaction_data.get("data", {}).get("userOperationHash")
        print(f"Transaction created successfully. ID: {transaction_id}")

        # Step 5: Generate signature
        print("\n5. Generating signature...")
        private_key = os.getenv('SIGNER_PRIVATE_KEY')
        signature = generate_signature(private_key, user_op_hash)
        print(f"Signature generated successfully: {signature[:20]}...")

        # Step 6: Submit signature
        print("\n6. Submitting signature...")
        signer_id = f"evm-keypair-{signer_address}"
        submit_response = submit_transaction_signature(
            api_key, 
            wallet1_address, 
            transaction_id, 
            signer_id, 
            signature
        )
        
        if submit_response.get("status") != "success":
            raise Exception("Signature submission failed")
            
        signing_status = submit_response.get("transaction_data", {}).get("signingData", {}).get("status", [])[0]
        if signing_status.get("status") != "completed":
            raise Exception("Signature was not properly recorded")
            
        print("Signature submitted and verified successfully")

        # Step 7: Verify transaction and final balances
        print("\n7. Verifying transaction and final balances...")
        time.sleep(10)
        
        transaction_status = get_transaction(api_key, wallet1_address, transaction_id)
        if transaction_status.get("status") != "success":
            raise Exception("Transaction verification failed")
        
        # Check final balances of both wallets
        print("\nChecking final balances...")
        wallet1_final = get_wallet_balance(api_key, "base-sepolia", wallet1_address)
        wallet2_final = get_wallet_balance(api_key, "base-sepolia", wallet2_address)
        
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
                "user_op_hash": user_op_hash,
                "signature": signature,
                "final_status": transaction_status,
                "wallet1_final_balance(currently not working, please check https://sepolia.basescan.org/address/{wallet1_address}#tokentxns for balance)": wallet1_final.get("balance"),
                "wallet2_final_balance(currently not working, please check https://sepolia.basescan.org/address/{wallet2_address}#tokentxns for balance)": wallet2_final.get("balance")
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