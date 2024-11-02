import os
import sys
from pathlib import Path
# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from library.wallet_utils import get_usdc_from_faucet, get_wallet_balance
from dotenv import load_dotenv

load_dotenv()

user_wallet_address = "your_wallet_address_here" 
chain = "base-sepolia"
amount = 4

if __name__ == "__main__":
    response = get_usdc_from_faucet(chain, user_wallet_address, amount)

    if response.get("status") == "success":
        api_key = os.getenv('CROSSMINT_SERVER_API_KEY')
        balance_response = get_wallet_balance(api_key, chain, user_wallet_address)
        if balance_response.get("status") == "success":
            token_balance = balance_response.get("wallet_data", {}).get("balance", "0x0")
            balance_decimal = int(token_balance, 16) / 10**6
            print(f"Wallet Balance: {balance_decimal} USDC")
        else:
            print(f"Error getting balance: {balance_response.get('error')}")
    else:
        print(f"Error: {response.get('error')}")

