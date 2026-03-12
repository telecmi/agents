# Phone Agent (Outbound Calling)

This example demonstrates how to implement a dedicated **Phone Agent** mapped to programmatic outbound calling.

## Requirements

You must install the SDK with the relevant provider extras:

```bash
pip install "piopiy-ai[cartesia,deepgram,openai,silero]" python-dotenv
pip install piopiy
```

Your `.env` file must contain these keys:

```bash
# Agent Process Setup
AGENT_ID="your_agent_id"
AGENT_TOKEN="your_agent_token"
OPENAI_API_KEY="your_openai_key"
DEEPGRAM_API_KEY="your_deepgram_key"
CARTESIA_API_KEY="your_cartesia_key"

# Required for Outbound Testing
PIOPIY_TOKEN="your_rest_api_token"
PIOPIY_NUMBER="your_purchased_number"
CUSTOMER_NUMBER="destination_phone_number"
```

## Running the Agent

Start the worker script to handle the pipeline streams:

```bash
python phone_agent.py
```

While the `phone_agent.py` script is running in one terminal, open a second terminal and trigger an outbound programmatic call:

```bash
python outbound_call.py
```

The REST API will dial the `CUSTOMER_NUMBER`. When the customer answers, they will be instantly connected to the Phone Agent with a dynamic, personalized context parameter (e.g. their name)!
