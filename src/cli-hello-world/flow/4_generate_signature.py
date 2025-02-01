import os
import sys
from pathlib import Path
# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from library.wallet_utils import generate_signature
from dotenv import load_dotenv

load_dotenv()

user_op_hash = "your_user_op_hash_here"


def generate_evm_smart_wallet_signature():
    try:
        private_key = os.getenv('SIGNER_PRIVATE_KEY')
        if not private_key:
            raise ValueError(
                "SIGNER_PRIVATE_KEY not found in environment variables")

        return generate_signature(private_key, user_op_hash)
    except ValueError as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    result = generate_evm_smart_wallet_signature()
    if isinstance(result, dict) and result.get("status") == "error":
        print(f"Error: {result.get('error')}")
    else:
        print(f"Signature: {result}")
