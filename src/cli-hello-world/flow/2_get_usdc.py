import os
import os
import sys
from pathlib import Path
# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from library.wallet_utils import get_usdc_from_faucet, get_wallet_balance
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('CROSSMINT_SERVER_API_KEY')
if not api_key:
    raise ValueError("No API key found in .env file")

user_wallet_address = "your_wallet_address_here"
chain = "base-sepolia"
amount = 4

if __name__ == "__main__":
    response = get_usdc_from_faucet(
        api_key, chain, user_wallet_address, amount)

    if response.get("status") == "success":
        api_key = os.getenv('CROSSMINT_SERVER_API_KEY')
        balance_response = get_wallet_balance(
            api_key, chain, user_wallet_address)
        if balance_response.get("status") == "success":
            print(f"Wallet Balance: {balance_response.get('balance')} USDC")
        else:
            print(f"Error getting balance: {balance_response.get('error')}")
    else:
        print(f"Error: {response.get('error')}")
