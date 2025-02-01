import os
import sys
import json
from pathlib import Path
# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from library.wallet_utils import submit_transaction_approval
from dotenv import load_dotenv

load_dotenv()


def submit_evm_smart_wallet_signature():
    api_key = os.getenv('CROSSMINT_SERVER_API_KEY')
    user_op_sender = "0x0364531237597B8694F3E63C2f8Db19f00BfBED1"
    transaction_id = "66a8e7a1-cfc3-4063-a9fb-216bbcf92bfc"
    signer_id = "0x94A4491f467bc21d7F280B1a3451CD1672F79088"
    # Signature generated from generate_signature.py
    signature = "0x27a517e00b90010ac2708fcfd6bc7d22657d924bcaaa36a6ca85bd661b8a21b2175dbca2788af96f41797939470df1de05d4ee0d4200d009c8b1f59aa51275271b"

    return submit_transaction_approval(api_key, user_op_sender, transaction_id, signer_id, signature)


if __name__ == "__main__":
    response = submit_evm_smart_wallet_signature()

    if response.get("status") == "success":
        print(f"\nTransaction Signed Successfully!")
    else:
        print(f"\nTransaction Signing Failed!")

    print(f"Result: {json.dumps(response, indent=2)}")
