# ai-agent-demos-python

## Setup Instructions

### src/cli-hello-world

1. Set up your API keys in `.env`:

   ```bash
   OPENAI_API_KEY=your_openai_key_here
   CROSSMINT_SERVER_API_KEY=your_crossmint_key_here
   ```

2. Generate encryption keys:

   ```bash
   cd src/library
   python3 generate_keys.py
   ```

3. Copy the generated public and private keys into your `.env` file:

   ```bash
   SIGNER_PRIVATE_KEY=generated_private_key_here
   SIGNER_ADDRESS=generated_public_key_here
   ```

4. Run the primary agent:
   ```bash
   cd src/cli-hello-world
   python3 run.py
   ```
