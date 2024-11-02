import os
import sys
from pathlib import Path
import json
import time
import random
from openai import OpenAI
from dotenv import load_dotenv

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from library.wallet_utils import (
    create_wallet, create_transaction, generate_signature, 
    submit_transaction_signature, get_transaction, 
    transfer_usdc, get_usdc_from_faucet, get_wallet_balance
)
from library.tools_schema import tools_schema

# Load environment variables
load_dotenv()

class CryptoAssistantAgent:
    def __init__(self):
        # Initialize OpenAI client and API keys
        self.client = OpenAI()
        self.api_key = os.getenv('CROSSMINT_SERVER_API_KEY')
        self.private_key = os.getenv('SIGNER_PRIVATE_KEY')
        self.signer_address = os.getenv('SIGNER_ADDRESS')
        
        if not all([self.api_key, self.private_key, self.signer_address]):
            raise ValueError("Missing required environment variables")
            
        self.wallets = []
        self.chain_explorers = {
            "base-sepolia": "https://sepolia.basescan.org",
            "ethereum-sepolia": "https://sepolia.etherscan.io",
            "solana-devnet": "https://explorer.solana.com/?cluster=devnet"
        }

    def create_new_wallet(self, wallet_type):
        """Agent method to create and track new wallets"""
        result = create_wallet(self.api_key, wallet_type, self.signer_address)
        
        if result.get("status") == "success":
            self.wallets.append(result["wallet_data"])
            
        return result

    def select_wallet(self):
        """Prompt user to select a wallet from their available wallets"""
        if not self.wallets:
            print("No wallets available. Please create a wallet first.")
            return None
        
        print("\nAvailable wallets:")
        for i, wallet in enumerate(self.wallets):
            print(f"{i+1}. {wallet['address']} (Type: {wallet['type']})")
        
        while True:
            try:
                choice = int(input("\nSelect wallet number: ")) - 1
                if 0 <= choice < len(self.wallets):
                    return self.wallets[choice]['address']
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

    def get_explorer_url(self, wallet_address: str, chain: str = "base-sepolia") -> str:
        """Generate blockchain explorer URL for the wallet"""
        base_url = self.chain_explorers.get(chain)
        if not base_url:
            return "Unknown chain explorer"
        
        if "solana" in chain:
            return f"{base_url}/address/{wallet_address}"
        else:
            return f"{base_url}/address/{wallet_address}#tokentxns"

    def get_wallet_balance(self, wallet_address):
        """Agent method to get the balance of a wallet"""
        wallet = next((w for w in self.wallets if w['address'] == wallet_address), None)
        if not wallet:
            return {"status": "error", "message": "Wallet not found in tracked wallets"}
            
        chain = "base-sepolia" if wallet['type'] == "evm-smart-wallet" else "solana-devnet"
        explorer_url = self.get_explorer_url(wallet_address, chain)
        
        return {
            "status": "success",
            "message": f"View wallet balance and transactions at: {explorer_url}",
            "explorer_url": explorer_url
        }

    def create_transaction(self, wallet_address):
        """Create and process a transaction for the specified wallet"""
        try:
            # Step 1: Create transaction
            print("\nCreating transaction...")
            transaction_response = create_transaction(self.api_key, wallet_address, "base-sepolia")
            
            if transaction_response.get("status") != "success":
                return {"status": "error", "message": "Transaction creation failed"}
                
            transaction_data = transaction_response.get("transaction_data", {})
            transaction_id = transaction_data.get("id")
            user_op_hash = transaction_data.get("data", {}).get("userOperationHash")
            
            # Step 2: Generate signature
            print("Generating signature...")
            signature = generate_signature(self.private_key, user_op_hash)
            
            # Step 3: Submit signature
            print("Submitting signature...")
            signer_id = f"evm-keypair-{self.signer_address}"
            submit_response = submit_transaction_signature(
                self.api_key, 
                wallet_address, 
                transaction_id, 
                signer_id, 
                signature
            )
            
            if submit_response.get("status") != "success":
                return {"status": "error", "message": "Signature submission failed"}
                
            # Step 4: Verify transaction
            print("Verifying transaction...")
            time.sleep(10)  # Allow transaction to process
            
            transaction_status = get_transaction(self.api_key, wallet_address, transaction_id)
            
            return {
                "status": "success",
                "message": "Transaction completed successfully",
                "data": {
                    "transaction_id": transaction_id,
                    "final_status": transaction_status
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_usdc_tokens(self, wallet_address: str, amount: int):
        """Get USDC tokens from faucet for a wallet"""
        result = get_usdc_from_faucet("base-sepolia", wallet_address, amount)
        
        if result.get("status") == "success":
            print(f"Waiting for faucet transaction to process...")
            time.sleep(5)
            
            # Provide explorer link instead of balance
            explorer_url = self.get_explorer_url(wallet_address)
            print(f"\nView your USDC balance and transactions at: {explorer_url}")
        
        return result

    def transfer_usdc_tokens(self, from_wallet: str, to_wallet: str, amount: int):
        """Transfer USDC tokens between wallets"""
        try:
            # Convert USDC amount to base units (1 USDC = 1,000,000 base units)
            amount_in_base_units = amount * 1000000

            # Create and send the transaction
            transaction_response = transfer_usdc(
                self.api_key,
                from_wallet,
                to_wallet,
                amount_in_base_units,
                "base-sepolia"
            )
            
            if transaction_response.get("status") != "success":
                return transaction_response

            transaction_data = transaction_response.get("transaction_data", {})
            transaction_id = transaction_data.get("id")
            user_op_hash = transaction_data.get("data", {}).get("userOperationHash")

            if not user_op_hash:
                return {
                    "status": "error",
                    "message": "No user operation hash found in transaction data"
                }

            # Generate and submit signature
            signature = generate_signature(self.private_key, user_op_hash)
            signer_id = f"evm-keypair-{self.signer_address}"
            
            submit_response = submit_transaction_signature(
                self.api_key,
                from_wallet,
                transaction_id,
                signer_id,
                signature
            )

            if submit_response.get("status") != "success":
                return submit_response

            # Wait for transaction to process
            print("Waiting for transaction to process...")
            time.sleep(15)  # Increased wait time

            # Get final transaction status and verify it
            transaction_status = get_transaction(self.api_key, from_wallet, transaction_id)
            
            if (transaction_status.get("status") == "success" and 
                transaction_status.get("transaction_data", {}).get("status") == "confirmed"):
                from_explorer = self.get_explorer_url(from_wallet)
                to_explorer = self.get_explorer_url(to_wallet)
                
                return {
                    "status": "success",
                    "message": "USDC transfer completed",
                    "data": {
                        "transaction_id": transaction_id,
                        "final_status": transaction_status,
                        "from_wallet_explorer": from_explorer,
                        "to_wallet_explorer": to_explorer
                    }
                }
            else:
                return {
                    "status": "error",
                    "message": "Transaction not confirmed on chain",
                    "data": transaction_status
                }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Transfer failed: {str(e)}"
            }

def main():
    try:
        agent = CryptoAssistantAgent()
        print("Welcome to the AI Assistant! (Type 'exit' or 'q' to quit)")

        # Create an assistant
        assistant = agent.client.beta.assistants.create(
            name="Web3 Assistant",
            instructions="""You are a super helpful AI web3 assistant that can perform actions on the blockchain using Crossmint's API.
            You can create new wallets, check balances, deposit tokens, transfer tokens between wallets, and more.""",
            tools=tools_schema(),
            model="gpt-4-turbo-preview"
        )

        # Create a thread for the conversation
        thread = agent.client.beta.threads.create()

        while True:
            user_input = input("\nAsk anything -> ").strip()
                
            if user_input.lower() in ['exit', 'q']:
                farewell = random.choice(["Goodbye!", "See ya!", "Take care!"])
                print(farewell)
                break

            # Create message in thread
            message = agent.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_input
            )

            # Create and process run
            run = agent.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id,
            )

            while True:
                run = agent.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                
                if run.status == 'completed':
                    messages = agent.client.beta.threads.messages.list(
                        thread_id=thread.id
                    )
                    # Display latest assistant message
                    latest_message = next(msg for msg in messages.data 
                                       if msg.role == "assistant")
                    print(f"\nAI Assistant: {latest_message.content[0].text.value}")
                    break
                    
                elif run.status == 'requires_action':
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    tool_outputs = []
                    
                    for tool_call in tool_calls:
                        args = json.loads(tool_call.function.arguments)
                        result = None
                        
                        # Handle different tool calls
                        if tool_call.function.name == "create_new_wallet":
                            result = agent.create_new_wallet(args["wallet_type"])
                            if result.get("status") == "success":
                                print(f"\nWallet Created Successfully!")
                            
                        elif tool_call.function.name == "get_wallet_balance":
                            result = agent.get_wallet_balance(args["wallet_address"])
                            if result.get("status") == "success":
                                print(f"\n{result.get('message')}")
                                
                        elif tool_call.function.name == "create_transaction":
                            wallet_address = agent.select_wallet()
                            if wallet_address:
                                result = agent.create_transaction(wallet_address)
                                if result.get("status") == "success":
                                    print("\nTransaction Completed Successfully!")
                                else:
                                    print(f"\nTransaction Failed: {result.get('message', 'Unknown error')}")

                        elif tool_call.function.name == "get_usdc_from_faucet":
                            result = agent.get_usdc_tokens(args["wallet_address"], args["amount"])
                            if result.get("status") == "success":
                                print("\nUSDC tokens requested successfully!")
                            else:
                                print(f"\nFailed to get USDC tokens: {result.get('message', 'Unknown error')}")

                        elif tool_call.function.name == "transfer_usdc":
                            result = agent.transfer_usdc_tokens(
                                args["from_wallet_address"],
                                args["to_wallet_address"],
                                args["amount"]
                            )
                            if result.get("status") == "success":
                                print("\nUSDC transfer completed successfully!")
                                print(f"\nView source wallet at: {result['data']['from_wallet_explorer']}")
                                print(f"View destination wallet at: {result['data']['to_wallet_explorer']}")
                            else:
                                print(f"\nUSDC transfer failed: {result.get('message', 'Unknown error')}")

                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(result)
                        })
                    
                    # Submit tool outputs
                    agent.client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
                    
                elif run.status in ['failed', 'expired']:
                    print(f"Run failed with status: {run.status}")
                    break
                
                time.sleep(1)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
