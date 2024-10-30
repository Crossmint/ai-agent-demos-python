from src.library.wallet_utils import create_wallet
from .agent_utils import create_openai_agent, AIAgent
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class SwarmAIAgent:
    def __init__(self, api_key=None, openai_key=None):
        self.api_key = api_key or os.getenv('CROSSMINT_API_KEY')
        self.openai_key = openai_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key or not self.openai_key:
            raise ValueError("Both Crossmint and OpenAI API keys are required")
        
        self.wallets = []
        openai_client = create_openai_agent(self.openai_key)
        self.ai_agent = AIAgent(openai_client)

    def create_new_wallet(self, wallet_type, signer_address):
        # Get AI-enhanced request
        enhanced_request = self.ai_agent.enhance_wallet_request(
            wallet_type, 
            signer_address
        )
        
        print(f"AI Recommendations: {enhanced_request.get('ai_recommendations')}")
        
        # Create wallet with enhanced parameters
        result = create_wallet(
            self.api_key, 
            enhanced_request["wallet_type"], 
            enhanced_request["signer_address"]
        )
        
        if result.get("status") == "success":
            self.wallets.append(result["wallet_data"])
            result["ai_analysis"] = self.ai_agent.analyze_wallet_creation(result)
            
        return result

def main():
    try:
        agent = SwarmAIAgent()
        print("Hello! Welcome to the OpenAI-enhanced wallet demo!")
        
        result = agent.create_new_wallet(
            wallet_type="evm-smart-wallet",
            signer_address="0x123...abc"
        )
        
        if result.get("status") == "success":
            print(f"Wallet created successfully!")
            print(f"Wallet data: {result['wallet_data']}")
            print(f"AI Analysis: {result.get('ai_analysis')}")
        else:
            print(f"Wallet creation failed: {result.get('error')}")
            
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()