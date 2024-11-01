## Setup Instructions

### src/openai_assistant-hello-world

1. Set up your API keys in `.env`:

   ```bash
   OPENAI_API_KEY=your_openai_key_here
   OPENAI_ORG_ID=your_openai_org_id_here
   OPENAI_PROJECT_ID=your_openai_project_id_here
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
   cd src/openai_assistant-hello-world
   pip3|pip install -r requirements.txt
   ```

5. From the `src/openai_assistant-hello-world` directory, run the primary agent:
   ```bash
   python3 run.py
   ```
