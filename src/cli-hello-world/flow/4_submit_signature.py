import os
import sys
import json
from pathlib import Path
# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from library.wallet_utils import submit_transaction_signature
from dotenv import load_dotenv

load_dotenv()


def submit_evm_smart_wallet_signature():
    api_key = os.getenv('CROSSMINT_SERVER_API_KEY')
    user_op_sender = "TODO:user_op_sender_address_here"
    transaction_id = "TODO:transaction_id_here"
    signer_id = "evm-keypair-TODO:signer_id_here"
    signature = "TODO:signature_here" # Signature generated from generate_signature.py

    return submit_transaction_signature(api_key, user_op_sender, transaction_id, signer_id, signature)

if __name__ == "__main__":
    response = submit_evm_smart_wallet_signature()

    if response.get("status") == "success":
        print(f"\nTransaction Signed Successfully!")
    else:
        print(f"\nTransaction Signing Failed!")
        
    print(f"Result: {json.dumps(response, indent=2)}")
