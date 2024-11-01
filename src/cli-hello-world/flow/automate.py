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
    create_transaction,
    generate_signature,
    submit_transaction_signature,
    get_transaction
)

load_dotenv()

def automate_wallet_flow():
    try:
        # Step 1: Create wallet
        print("\n1. Creating EVM Smart Wallet...")
        api_key = os.getenv('CROSSMINT_SERVER_API_KEY')
        signer_address = os.getenv('SIGNER_ADDRESS')
        wallet_response = create_wallet(api_key, "evm-smart-wallet", signer_address)
        
        if wallet_response.get("status") != "success":
            raise Exception("Wallet creation failed")
        
        wallet_address = wallet_response.get("wallet_data", {}).get("address")
        signer_address = wallet_response.get("wallet_data", {}).get("config", {}).get("signer", {}).get("address")
        print(f"Wallet created successfully: {wallet_address}")

        # Step 2: Create transaction
        print("\n2. Creating transaction...")
        transaction_response = create_transaction(api_key, wallet_address, "base-sepolia")
        
        if transaction_response.get("status") != "success":
            raise Exception("Transaction creation failed")
            
        transaction_data = transaction_response.get("transaction_data", {})
        transaction_id = transaction_data.get("id")
        user_op_hash = transaction_data.get("data", {}).get("userOperationHash")
        print(f"Transaction created successfully. ID: {transaction_id}")

        # Step 3: Generate signature
        print("\n3. Generating signature...")
        private_key = os.getenv('SIGNER_PRIVATE_KEY')
        signature = generate_signature(private_key, user_op_hash)
        print(f"Signature generated successfully: {signature[:20]}...")

        # Step 4: Submit signature
        print("\n4. Submitting signature...")
        signer_id = f"evm-keypair-{signer_address}"
        submit_response = submit_transaction_signature(
            api_key, 
            wallet_address, 
            transaction_id, 
            signer_id, 
            signature
        )
        
        if submit_response.get("status") != "success":
            raise Exception("Signature submission failed")
            
        # Check if signature was properly recorded
        signing_status = submit_response.get("transaction_data", {}).get("signingData", {}).get("status", [])[0]
        if signing_status.get("status") != "completed":
            raise Exception("Signature was not properly recorded")
            
        print("Signature submitted and verified successfully")

        # Step 5: Verify transaction
        print("\n5. Verifying transaction...")
        # Add a delay to allow the transaction to process
        time.sleep(10)  # Adjust based on typical processing time
        
        transaction_status = get_transaction(api_key, wallet_address, transaction_id)
        if transaction_status.get("status") != "success":
            raise Exception("Transaction verification failed")
        
        return {
            "status": "success",
            "message": "Wallet flow completed successfully",
            "data": {
                "wallet_address": wallet_address,
                "transaction_id": transaction_id,
                "user_op_hash": user_op_hash,
                "signature": signature,
                "final_status": transaction_status
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