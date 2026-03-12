# Tool Calling Agent

This example provides a clear implementation of integrating external functions into your Piopiy Voice Agent by defining custom Python functions as "tools".

The LLM is instructed to use a `get_current_weather` tool when the caller asks about the weather. When triggered, the LLM stops speaking, your local Python function executes with extracted entity arguments (like the City), and the JSON result is fed back to the LLM to generate a natural voice response.

## Requirements

You must install the SDK with the relevant provider extras:

```bash
pip install "piopiy-ai[cartesia,deepgram,openai,silero]"
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

Start the worker script to handle incoming calls:

```bash
python tool_calling_agent.py
```

1. Log in to the **[Piopiy Dashboard](https://dashboard.telecmi.com)**.
2. Ensure you have purchased a Piopiy phone number and mapped it to your new AI Agent.
3. **Dial that phone number** from your personal phone to interact with your local agent!

When the agent picks up, ask it: *"What is the weather like in New York right now?"*
