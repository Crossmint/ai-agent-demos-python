## Setup Instructions

### src/cli-hello-world

1. Set up your API keys in `.env`:

   ```bash
   OPENAI_API_KEY=your_openai_key_here
   CROSSMINT_SERVER_API_KEY=your_crossmint_key_here
   ```

2. Generate public/private keypair:

   ```bash
   cd src/library
   python3 generate_keys.py
   ```

3. Copy the generated public/private keypair into your `.env` file:

   ```bash
   SIGNER_PRIVATE_KEY=generated_private_key_here
   SIGNER_ADDRESS=generated_public_key_here
   ```

4. Install required Python packages:

   ```bash
   cd src/cli-hello-world
   pip3|pip install -r requirements.txt
   ```

5. From the `src/cli-hello-world` directory, run the primary agent:
   ```bash
   python3 run.py
   ```

# Crossmint Wallet API Demo

This project demonstrates two distinct ways to interact with Crossmint's Wallet API:

## 1. Basic Automation Flow (/flow/automate.py)

A straightforward script that demonstrates the basic wallet operations in sequence:

- Creates two wallets
- Wallet 1 is funded with USDC from faucet
- Wallet 1 transfers USDC to Wallet 2
- Handles signatures
- Verifies transactions
- Checks final balances of both wallets
- Wallet 2 is funded with USDC from Wallet 1

Run with:

```bash
python|python3 src/cli-hello-world/flow/automate.py
```

## 2. AI-Powered Agent (run.py)

An intelligent agent powered by OpenAI's GPT model that:

- Interprets natural language commands
- Dynamically plans and executes wallet operations
- Provides conversational responses
- Can handle complex, multi-step operations
- Adapts to user requests in real-time

Run with:

```bash
python|python3 src/cli-hello-world/run.py
```

Example commands for AI agent:

- "Create a new evm smart wallet"
- "Fund my wallet with 10 USDC"
- "Check my wallet balance"
- "Transfer 2 USDC to address 0x..."
