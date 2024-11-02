# !! OUR GET WALLET BALANCE ENDPOINT IS CURRENTLY NOT WORKING :( !!

import os
import sys
from pathlib import Path
# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from library.wallet_utils import get_wallet_balance
from dotenv import load_dotenv

load_dotenv()

user_wallet_address = "0x5B20a88375A7ae6D3D1efAe9a86CC7225006518d" 
chain = "ethereum-sepolia"

if __name__ == "__main__":
    api_key = os.getenv('CROSSMINT_SERVER_API_KEY')
    balance_response = get_wallet_balance(api_key, chain, user_wallet_address)
    
    if balance_response.get("status") == "success":
        print(f"Wallet Address: {user_wallet_address}")
        # print(f"Balance: {balance_response.get('balance')} USDC")
        print("get wallet balance doesn't work yet!")
    else:
        print(f"Error getting balance: {balance_response.get('error')}")
