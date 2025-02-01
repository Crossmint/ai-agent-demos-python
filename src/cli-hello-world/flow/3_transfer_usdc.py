import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from library.wallet_utils import transfer_usdc

from dotenv import load_dotenv

load_dotenv()


def transfer_usdc_to_wallet():
    api_key = os.getenv('CROSSMINT_SERVER_API_KEY')
    private_key = os.getenv('SIGNER_PRIVATE_KEY')
    from_wallet_address = "your_wallet_address_here"
    to_wallet_address = "your_wallet_address_here"
    amount = 1000000  # 1 USDC

    response = transfer_usdc(
        api_key=api_key,
        from_wallet_address=from_wallet_address,
        to_wallet_address=to_wallet_address,
        amount=amount,
        private_key=private_key
    )

    return response


if __name__ == "__main__":
    response = transfer_usdc_to_wallet()
    print(response)
