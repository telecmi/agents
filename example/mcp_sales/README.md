# MCP Knowledge Agent (Sales)

This example demonstrates how to give your Voice Agent access to external, structured data using the **Model Context Protocol (MCP)**. 

By injecting an MCP client into the Voice Agent, the LLM can dynamically search a document base (like Notion, a local SQLite database, or an internal API) mid-conversation without needing complex custom function definitions.

## Requirements

Install the SDK with the relevant provider extras:

```bash
pip install "piopiy-ai[cartesia,deepgram,openai,silero]"
```

Additionally, you will need an MCP server running. This example is configured to connect to a server via **SSE** (Server-Sent Events), but Piopiy also supports **Stdio**.

## Environment Setup

Ensure your `.env` file contains your API keys and Agent credentials:

```bash
# Required
AGENT_ID="your_agent_id"
AGENT_TOKEN="your_agent_token"

# Provider API Keys
OPENAI_API_KEY="your_openai_key"
DEEPGRAM_API_KEY="your_deepgram_key"
CARTESIA_API_KEY="your_cartesia_key"
```

## Running the Agent

Start the worker script to handle incoming calls:

```bash
python mcp_sales.py
```

1. Log in to the **[Piopiy Dashboard](https://dashboard.telecmi.com)**.
2. Ensure you have purchased a Piopiy phone number and mapped it to your new AI Agent.
3. **Dial that phone number** from your personal phone to interact with your local agent!

*Ask the agent questions about your specific business data—it will use MCP to search your connected data sources!*
