import os
import sys
from pathlib import Path
import json
# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from library.wallet_utils import create_wallet
from dotenv import load_dotenv

load_dotenv()


def create_evm_smart_wallet():
    api_key = os.getenv('CROSSMINT_SERVER_API_KEY')
    signer_address = os.getenv('SIGNER_ADDRESS')
    return create_wallet(api_key, "evm-smart-wallet", signer_address)


if __name__ == "__main__":
    response = create_evm_smart_wallet()
    if response.get("status") == "success":
        print(f"\nWallet Created Successfully!")
    else:
        print(f"\nWallet Creation Failed!")

    print(f"Result: {json.dumps(response, indent=2)}")
