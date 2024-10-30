from src.library.wallet_utils import create_wallet
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class CryptoAIAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('CROSSMINT_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required. Set CROSSMINT_API_KEY environment variable or pass it directly.")
        self.wallets = []

    def create_new_wallet(self, wallet_type, signer_address):
        """Agent method to create and track new wallets"""
        result = create_wallet(self.api_key, wallet_type, signer_address)
        
        if result.get("status") == "success":
            self.wallets.append(result["wallet_data"])
            
        return result
    
    def get_wallet_count(self):
        """Track number of wallets created"""
        return len(self.wallets)

def main():
    try:
        # Initialize the agent
        agent = CryptoAIAgent()
        
        print("Hello! Welcome to the basic wallet demo!")
        
        # Example: Create a new wallet
        result = agent.create_new_wallet(
            wallet_type="evm-smart-wallet",
            signer_address="0x123...abc"
        )
        
        # Check the result
        if result.get("status") == "success":
            print(f"Wallet created successfully!")
            print(f"Total wallets: {agent.get_wallet_count()}")
            print(f"Wallet data: {result['wallet_data']}")
        else:
            print(f"Wallet creation failed: {result.get('error')}")
            
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()