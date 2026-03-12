# Call Transfer Agent

This example demonstrates how to perform a **Live Call Transfer** using the Piopiy Voice SDK and REST Client.

When the customer asks to speak with a human or a supervisor, the AI Agent uses a Tool Call to trigger the `RestClient.voice.transfer()` method. This sends a command to the Piopiy cloud to re-route the active call to a different phone number or SIP destination.

## Requirements

Install the SDK with the relevant provider extras:

```bash
pip install "piopiy-ai[cartesia,deepgram,openai,silero]"
pip install piopiy
```

## Environment Setup

Ensure your `.env` file contains your credentials:

```bash
# Agent Process Setup
AGENT_ID="your_agent_id"
AGENT_TOKEN="your_agent_token"
OPENAI_API_KEY="your_openai_key"
DEEPGRAM_API_KEY="your_deepgram_key"
CARTESIA_API_KEY="your_cartesia_key"

# Required for Transfer
PIOPIY_TOKEN="your_rest_api_token"
TRANSFER_NUMBER="+15550001122" # The number you want to transfer to
```

## Running the Agent

Start the worker script to handle incoming calls:

```bash
python call_transfer_agent.py
```

1. Log in to the **[Piopiy Dashboard](https://dashboard.telecmi.com)**.
2. Ensure you have purchased a Piopiy phone number and mapped it to your new AI Agent.
3. **Dial that phone number** from your personal phone.

Once the call is active, say something like: *"I'd like to talk to a manager please."*

The agent will acknowledge your request and immediately trigger the transfer!
