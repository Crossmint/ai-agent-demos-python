import time
import json
from openai import OpenAI
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from library.tools_schema import tools_schema
from library.wallet_utils import (
    create_wallet,
    create_transaction, generate_signature, submit_transaction_approval,
    get_transaction, transfer_usdc, get_usdc_from_faucet
)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class CryptoAIAgent:
    def __init__(self):
        self.api_key = os.getenv('CROSSMINT_SERVER_API_KEY')
        if not self.api_key:
            raise ValueError("No API key found in .env file")

        self.private_key = os.getenv('SIGNER_PRIVATE_KEY')
        if not self.private_key:
            raise ValueError("No signer private key found in .env file")

        self.signer_address = os.getenv('SIGNER_ADDRESS')
        if not self.signer_address:
            raise ValueError(
                "No signer address found in .env file, be sure to run 'python generate_keys.py' inside '/src/library' to generate a new set of keys")

        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("No OpenAI API key found in .env file")

        self.evm_treasury_wallet = os.getenv('TEST_TREASURY_EVM_WALLET')

        self.chain_explorers = {
            "base-sepolia": "https://sepolia.basescan.org",
            "ethereum-sepolia": "https://sepolia.etherscan.io",
            "solana-devnet": "https://explorer.solana.com/?cluster=devnet"
        }
        self.chat_history = []
        self.openai_client = OpenAI()
        self.wallets = []
        self.api_calls = 0
        self.max_api_calls = 20

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

    def create_transaction(self, wallet_address):
        """Create and process a transaction for the specified wallet"""
        try:
            # Step 1: Create transaction
            print("\nCreating transaction...")
            transaction_response = create_transaction(
                self.api_key, wallet_address, "base-sepolia")

            if transaction_response.get("status") != "success":
                return {"status": "error", "message": "Transaction creation failed"}

            transaction_data = transaction_response.get("transaction_data", {})
            transaction_id = transaction_data.get("id")
            user_op_hash = transaction_data.get(
                "data", {}).get("userOperationHash")

            # Step 2: Generate signature
            print("Generating signature...")
            signature = generate_signature(self.private_key, user_op_hash)

            # Step 3: Submit signature
            print("Submitting signature...")
            signer_id = self.signer_address
            submit_response = submit_transaction_approval(
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

            transaction_status = get_transaction(
                self.api_key, wallet_address, transaction_id)

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
        wallet = next(
            (w for w in self.wallets if w['address'] == wallet_address), None)
        if not wallet:
            return {"status": "error", "message": "Wallet not found in tracked wallets"}

        chain = "base-sepolia" if wallet['type'] == "evm-smart-wallet" else "solana-devnet"
        explorer_url = self.get_explorer_url(wallet_address, chain)

        return {
            "status": "success",
            "message": f"View wallet balance and transactions at: {explorer_url}",
            "explorer_url": explorer_url
        }

    def get_usdc_tokens(self, wallet_address: str, amount: int):
        """Get USDC tokens from faucet for a wallet"""
        result = get_usdc_from_faucet(
            self.api_key, "base-sepolia", wallet_address, amount)

        if result.get("status") == "success":
            print(f"Waiting for faucet transaction to process...")
            time.sleep(5)

            # Provide explorer link instead of balance
            explorer_url = self.get_explorer_url(wallet_address)
            print(f"\nView your USDC balance and transactions at: {
                  explorer_url}")

        return result

    def transfer_usdc_tokens(self, from_wallet: str, to_wallet: str, amount: int):
        """Transfer USDC tokens between wallets"""
        # Convert USDC amount to base units (1 USDC = 1,000,000 base units)
        amount_in_base_units = amount * 1000000

        # Create and send the transaction
        transaction_response = transfer_usdc(
            self.api_key,
            from_wallet,
            to_wallet,
            amount_in_base_units,
            "base-sepolia",
            self.private_key
        )

        if transaction_response.get("status") != "success":
            return transaction_response

        transaction_data = transaction_response.get("transaction_data", {})

        # Wait for transaction to process
        print("Waiting for transaction to process...")
        time.sleep(10)

        # Get the explorer URL for both wallets
        from_explorer = self.get_explorer_url(from_wallet)
        to_explorer = self.get_explorer_url(to_wallet)

        return {
            "status": "success",
            "message": "USDC transfer completed",
            "data": {
                "transaction_data": transaction_data,
                "from_wallet_explorer": from_explorer,
                "to_wallet_explorer": to_explorer
            }
        }

    def chat_completion(self, user_input):
        """Handle chat completion with OpenAI"""
        if self.api_calls >= self.max_api_calls:
            raise Exception(
                "Maximum API calls reached. Please restart the program.")

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

        You can create new wallets, check the balance of existing wallets, deposit tokens to a wallet, transfer tokens between wallets, and more."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": contextual_prompt},
                {"role": "user", "content": user_input}
            ],
            tools=tools_schema(),
            tool_choice="auto"
        )
        return response.choices[0].message


def main():
    try:
        agent = CryptoAIAgent()
        print("Welcome to the AI Agent! (Type 'exit' or 'q' to quit)")
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
                print(f"\nAI Agent: {response.content}")

            # Handle function calls
            if response.tool_calls:
                for tool_call in response.tool_calls:
                    if tool_call.function.name == "create_new_wallet":
                        # Parse JSON string into dict
                        args = json.loads(tool_call.function.arguments)
                        result = agent.create_new_wallet(args["wallet_type"])
                        if result.get("status") == "success":
                            print(f"\nWallet Created Successfully!")
                        else:
                            print(f"\nWallet Creation Failed!")

                        print(f"Result: {json.dumps(result, indent=2)}")

                    elif tool_call.function.name == "get_wallet_balance":
                        args = json.loads(tool_call.function.arguments)
                        result = agent.get_wallet_balance(
                            args["wallet_address"])
                        if result.get("status") == "success":
                            print(f"\n{result.get('message')}")
                        else:
                            print(f"\nError: {result.get('message')}")

                    elif tool_call.function.name == "create_transaction":
                        args = json.loads(tool_call.function.arguments)
                        wallet_address = agent.select_wallet()  # Let user select the wallet
                        if wallet_address:
                            result = agent.create_transaction(wallet_address)
                            if result.get("status") == "success":
                                print("\nTransaction Completed Successfully!")
                            else:
                                print(f"\nTransaction Failed: {
                                      result.get('message', 'Unknown error')}")
                            print(f"Result: {json.dumps(result, indent=2)}")
                        else:
                            print("\nNo wallet selected for transaction.")

                    elif tool_call.function.name == "get_usdc_from_faucet":
                        args = json.loads(tool_call.function.arguments)
                        result = agent.get_usdc_tokens(
                            args["wallet_address"], args["amount"])
                        if result.get("status") == "success":
                            print("\nUSDC tokens requested successfully!")
                        else:
                            print(f"\nFailed to get USDC tokens: {
                                  result.get('message', 'Unknown error')}")

                    elif tool_call.function.name == "transfer_usdc":
                        args = json.loads(tool_call.function.arguments)
                        result = agent.transfer_usdc_tokens(
                            args["from_wallet_address"],
                            args["to_wallet_address"],
                            args["amount"]
                        )
                        if result.get("status") == "success":
                            print("\nUSDC transfer completed successfully!")
                            print(f"\nView source wallet at: {
                                  result['data']['from_wallet_explorer']}")
                            print(f"View destination wallet at: {
                                  result['data']['to_wallet_explorer']}")
                        else:
                            print(f"\nUSDC transfer failed: {
                                  result.get('message', 'Unknown error')}")
                        print(f"Result: {json.dumps(result, indent=2)}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
