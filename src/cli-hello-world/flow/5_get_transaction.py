import os
import sys
import json
from pathlib import Path
# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from library.wallet_utils import get_transaction
from dotenv import load_dotenv

load_dotenv()

def fetch_transaction():
    api_key = os.getenv('CROSSMINT_SERVER_API_KEY')
    user_op_sender = "TODO:user_op_sender_address_here"
    transaction_id = "TODO:transaction_id_here"
    
    return get_transaction(api_key, user_op_sender, transaction_id)

if __name__ == "__main__":
    response = fetch_transaction()

    if response.get("status") == "success":
        print(f"\nTransaction Fetched Successfully!")
    else:
        print(f"\nTransaction Fetching Failed!")
        
    print(f"Result: {json.dumps(response, indent=2)}")
