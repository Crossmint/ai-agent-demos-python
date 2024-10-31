from web3 import Web3

def generate_keys():
    # Initialize Web3
    w3 = Web3()

    # Create a new account
    account = w3.eth.account.create()

    print(f"SIGNER_PRIVATE_KEY={account.key.hex()}")
    print(f"SIGNER_ADDRESS={account.address}")
    print("Be sure to copy and paste these values into your .env file")

if __name__ == "__main__":
    generate_keys()