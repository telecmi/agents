# Voice Assistant Example

This example provides a clean, ready-to-use template for a general-purpose AI voice assistant.

## Requirements

You must install the SDK with the relevant provider extras:

```bash
pip install "piopiy-ai[cartesia,deepgram,openai,silero]" python-dotenv
```

Your `.env` file must contain these keys:

```bash
AGENT_ID="your_agent_id"
AGENT_TOKEN="your_agent_token"
OPENAI_API_KEY="your_openai_key"
DEEPGRAM_API_KEY="your_deepgram_key"
CARTESIA_API_KEY="your_cartesia_key"
```

## Running the Agent

```bash
python voice_assistant.py
```
