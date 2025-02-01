import os
import sys
from pathlib import Path
import json
# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from library.wallet_utils import create_transaction
from dotenv import load_dotenv

load_dotenv()

# Update with your wallet address
test_wallet_address = "TODO:wallet_address_here"


def create_evm_smart_wallet_transaction():
    api_key = os.getenv('CROSSMINT_SERVER_API_KEY')
    return create_transaction(api_key, test_wallet_address, "base-sepolia")


if __name__ == "__main__":
    response = create_evm_smart_wallet_transaction()

    if response.get("status") == "success":
        print(f"\nTransaction Created Successfully!")
    else:
        print(f"\nTransaction Creation Failed!")

    print(f"Result: {json.dumps(response, indent=2)}")
