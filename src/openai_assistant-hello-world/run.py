import os
import sys
import time
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from library.wallet_utils import create_wallet
from library.tools_schema import tools_schema

from dotenv import load_dotenv
from openai import OpenAI
import os
import json

# Load environment variables
load_dotenv()

class AssistanceAgent:
    def __init__(self):
        self.crossmint_api_key = os.getenv('CROSSMINT_SERVER_API_KEY')
        if not self.crossmint_api_key:
            raise ValueError("No API key found in .env file")
        
        self.signer_address = os.getenv('SIGNER_ADDRESS')
        if not self.signer_address:
            raise ValueError("No signer address found in .env file, be sure to run 'python generate_keys.py' inside '/src/library' to generate a new set of keys")
        
        self.chat_history = []
        self.openai_client = OpenAI()  # Assumes OPENAI_API_KEY in env
        self.wallets = []
        self.api_calls = 0
        self.max_api_calls = 20

        self.client = OpenAI()

    def create_new_wallet(self, wallet_type):
        """Agent method to create and track new wallets"""
        result = create_wallet(self.crossmint_api_key, wallet_type, self.signer_address)
        
        if result.get("status") == "success":
            self.wallets.append(result["wallet_data"])
            
        return result


def main():
    try:
        agent = AssistanceAgent()
        print("Welcome to the AI Assistant! (Type 'exit' or 'q' to quit)")

        assistant = agent.client.beta.assistants.create(
            name="Web3 Assistant",
            instructions="You are a super helpful AI web3 assistant that can perform actions on the blockchain using Crossmint's API. You can create wallets and more!",
            tools=tools_schema(),
            model="gpt-4o-mini",
        )
        thread = agent.client.beta.threads.create()

        while True:
            user_input = input("\nAsk anything -> ").strip()
                
            if user_input.lower() in ['exit', 'q']:
                import random
                farewell = random.choice(["Goodbye!", "See ya!", "Take care!"])
                print(farewell)
                break

            # Create the message first
            message = agent.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_input
            )

            # Create run and handle it manually
            run = agent.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id,
            )

            # Polling loop to handle run status
            while True:
                run = agent.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                
                if run.status == 'completed':
                    messages = agent.client.beta.threads.messages.list(
                        thread_id=thread.id
                    )
                    for message in messages.data:
                        if message.role == "assistant":
                            print(message.content[0].text.value)
                    break
                elif run.status == 'requires_action':
                    # Handle tool calls
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    tool_outputs = []
                    
                    for tool_call in tool_calls:
                        if tool_call.function.name == "create_new_wallet":
                            args = json.loads(tool_call.function.arguments)  # Parse JSON string into dict
                            result = agent.create_new_wallet(args["wallet_type"])

                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": f"Wallet created successfully: {result}"
                            })
                    
                    # Submit tool outputs back to the run
                    agent.client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
                elif run.status in ['failed', 'expired']:
                    print(f"Run failed with status: {run.status}")
                    break
                
                time.sleep(1)  # Add a small delay between polling

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
