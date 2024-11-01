import os
import sys
from pathlib import Path
# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from library.wallet_utils import generate_signature
from dotenv import load_dotenv

load_dotenv()

user_op_hash = "TODO:user_op_hash_here" 

def generate_evm_smart_wallet_signature():
    private_key = os.getenv('SIGNER_PRIVATE_KEY')
    return generate_signature(private_key, user_op_hash)

if __name__ == "__main__":
    signature = generate_evm_smart_wallet_signature()
    print(f"Signature: {signature}")

