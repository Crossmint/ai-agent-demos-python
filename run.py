from wallet_utils import create_wallet

class CryptoAIAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.wallets = []  # Track created wallets
    
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
    # Initialize the agent
    agent = CryptoAIAgent(api_key="your_crossmint_api_key_here")
    
    # Example: Create a new wallet
    result = agent.create_new_wallet(
        wallet_type="evm-smart-wallet",
        signer_address="0x123...abc"
    )
    
    # Check the result
    if result.get("status") == "success":
        print(f"Wallet created successfully!")
        print(f"Total wallets: {agent.get_wallet_count()}")
    else:
        print(f"Wallet creation failed: {result.get('error')}")

if __name__ == "__main__":
    main()