import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from library.wallet_utils import create_wallet
from dotenv import load_dotenv
from openai import OpenAI
import os
import json

# Load environment variables
load_dotenv()

class CryptoAIAgent:
    def __init__(self):
        self.api_key = os.getenv('CROSSMINT_SERVER_API_KEY')
        if not self.api_key:
            raise ValueError("No API key found in .env file")
        
        self.signer_address = os.getenv('SIGNER_ADDRESS')
        if not self.signer_address:
            raise ValueError("No signer address found in .env file, be sure to run 'python generate_keys.py' inside '/src/library' to generate a new set of keys")
        
        self.chat_history = []
        self.openai_client = OpenAI()  # Assumes OPENAI_API_KEY in env
        self.wallets = []
        self.api_calls = 0
        self.max_api_calls = 20

    def create_new_wallet(self, wallet_type):
        """Agent method to create and track new wallets"""
        result = create_wallet(self.api_key, wallet_type, self.signer_address)
        
        if result.get("status") == "success":
            self.wallets.append(result["wallet_data"])
            
        return result
    
    def get_wallet_count(self):
        """Track number of wallets created"""
        return len(self.wallets)

    def get_tools_schema(self):
        """Define the available functions for the AI"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_new_wallet",
                    "description": "Creates a new blockchain wallet",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "wallet_type": {
                                "type": "string",
                                "enum": ["evm-smart-wallet", "solana-custodial-wallet"],
                                "description": "The type of wallet to create"
                            },
                        },
                        "required": ["wallet_type"]
                    }
                }
            },
        ]

    def chat_completion(self, user_input):
        """Handle chat completion with OpenAI"""
        if self.api_calls >= self.max_api_calls:
            raise Exception("Maximum API calls reached. Please restart the program.")
        
        self.api_calls += 1


        # Create wallet context
        wallet_context = "No wallets created yet."
        if self.wallets:
            wallet_details = [f"Wallet {i+1}: {w.get('address', 'No address')} (Type: {w.get('type', 'unknown')})" 
                            for i, w in enumerate(self.wallets)]
            wallet_context = "Available wallets:\n" + "\n".join(wallet_details)

        # Base contextual prompt where we include any wallet context
        contextual_prompt = f"""You are a super helpful AI web3 assistant that can perform actions on the blockchain using Crossmint's API.

        Current wallet status:
        {wallet_context}

        You can create new wallets, check the balance of existing wallets, list existing wallets, and more."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": contextual_prompt},
                {"role": "user", "content": user_input}
            ],
            tools=self.get_tools_schema(),
            tool_choice="auto"
        )
        return response.choices[0].message

def main():
    try:
        agent = CryptoAIAgent()
        print("Welcome to the AI Assistant! (Type 'exit' or 'q' to quit)")
        print(f"Maximum API calls: {agent.max_api_calls}")

        while True:
            user_input = input("\nAsk anything -> ").strip()
            
            if user_input.lower() in ['exit', 'q']:
                import random
                farewell = random.choice(["Goodbye!", "See ya!", "Take care!"])
                print(farewell)
                break
            
            # Get AI response
            response = agent.chat_completion(user_input)
            
            # Handle normal response
            if response.content:
                print(f"\nAI Assistant: {response.content}")

            # Handle function calls
            if response.tool_calls:
                for tool_call in response.tool_calls:
                    if tool_call.function.name == "create_new_wallet":
                        args = json.loads(tool_call.function.arguments)  # Parse JSON string into dict
                        result = agent.create_new_wallet(args["wallet_type"])
                        if result.get("status") == "success":
                            print(f"\nWallet Created Successfully!")
                        else:
                            print(f"\nWallet Creation Failed!")
                            
                        print(f"Result: {json.dumps(result, indent=2)}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()