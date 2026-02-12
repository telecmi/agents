# MCP Sales Agent Example

This example demonstrates how to build a sales assistant with **Model Context Protocol (MCP)** integration for function calling and knowledge retrieval.

## What This Example Does

Creates an intelligent sales agent that can:
- Answer questions about products
- Look up customer information
- Access knowledge bases via MCP
- Call external functions/tools
- Provide personalized recommendations

## What is MCP?

Model Context Protocol (MCP) is an open protocol that enables AI models to securely access external data sources and tools. It allows your agent to:
- Query databases
- Access APIs
- Retrieve documents
- Execute functions
- Maintain context across conversations

## Installation

```bash
# Install Piopiy with MCP support
pip install "piopiy-ai[cartesia,deepgram,openai,silero,mcp]"
```

## Environment Variables

Create a `.env` file:

```bash
# Required
AGENT_ID=your_agent_id
AGENT_TOKEN=your_agent_token

# Provider API Keys
OPENAI_API_KEY=your_openai_key
DEEPGRAM_API_KEY=your_deepgram_key
CARTESIA_API_KEY=your_cartesia_key

# MCP Configuration (optional)
MCP_SERVER_URL=your_mcp_server_url

# Optional
AGENT_DEBUG=false
```

## Running the Example

```bash
python example/mcp_sales/mcp_sales.py
```

## How It Works

### 1. Define MCP Tools

```python
# Define available tools for the agent
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_product_info",
            "description": "Get detailed product information",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "Product ID"
                    }
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_inventory",
            "description": "Check product inventory",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"}
                }
            }
        }
    }
]
```

### 2. Configure LLM with Tools

```python
llm = OpenAILLMService(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini",
    tools=tools  # Enable function calling
)
```

### 3. Handle Function Calls

```python
async def handle_function_call(function_name, arguments):
    if function_name == "get_product_info":
        product_id = arguments.get("product_id")
        # Query your database or API
        return {
            "name": "Premium Widget",
            "price": 99.99,
            "in_stock": True
        }
    elif function_name == "check_inventory":
        # Check inventory system
        return {"quantity": 42}
```

## Use Cases

### Sales Assistant
```python
voice_agent = VoiceAgent(
    instructions="""You are a sales assistant for TechCorp.
    - Help customers find products
    - Check inventory availability
    - Provide pricing information
    - Answer product questions
    Use the available tools to look up real-time information.""",
    greeting="Hello! Welcome to TechCorp. How can I help you today?",
)
```

### Customer Support
```python
voice_agent = VoiceAgent(
    instructions="""You are a customer support agent.
    - Look up customer orders
    - Check order status
    - Process returns
    - Answer account questions
    Always verify customer identity before accessing their data.""",
    greeting="Thank you for calling support. May I have your account number?",
)
```

### Appointment Booking
```python
voice_agent = VoiceAgent(
    instructions="""You are an appointment booking assistant.
    - Check available time slots
    - Book appointments
    - Send confirmations
    - Handle rescheduling
    Be friendly and confirm all details before booking.""",
    greeting="Hi! I can help you schedule an appointment. What service are you interested in?",
)
```

## MCP Integration

### Connect to MCP Server

```python
from piopiy.services.mcp import MCPClient

# Initialize MCP client
mcp_client = MCPClient(
    server_url=os.getenv("MCP_SERVER_URL"),
    api_key=os.getenv("MCP_API_KEY")
)

# Use in your agent
async def create_session(...):
    # Agent can now access MCP resources
    knowledge = await mcp_client.query("product_catalog")
```

### Available MCP Resources

- **Databases**: Query SQL/NoSQL databases
- **APIs**: Call REST/GraphQL endpoints
- **Documents**: Search knowledge bases
- **Files**: Access file systems
- **Custom**: Your own MCP servers

## Advanced Features

### Context Management

```python
# Pre-populate conversation context
initial_messages = [
    {"role": "system", "content": "You are a sales expert."},
    {"role": "user", "content": "I'm interested in laptops."},
    {"role": "assistant", "content": "Great! Let me show you our laptop selection."}
]

voice_agent = VoiceAgent(
    instructions="...",
    greeting="Welcome back! Ready to continue?",
    initial_messages=initial_messages
)
```

### Dynamic Tool Loading

```python
# Load tools based on user context
if metadata and metadata.get("customer_tier") == "premium":
    tools.append(premium_customer_tools)
```

## Next Steps

- **[Function Calling Examples](../function_calling/)** - More tool examples
- **[Basic Example](../basic/)** - Start simpler
- **[MCP Documentation](https://modelcontextprotocol.io)** - Learn more about MCP

## Troubleshooting

### Function calls not working
- Verify OpenAI API key has function calling access
- Check tool definitions match OpenAI schema
- Enable `AGENT_DEBUG=true` to see function call logs

### MCP connection issues
- Verify MCP server URL is correct
- Check MCP server is running
- Ensure network connectivity

## Resources

- [MCP Official Site](https://modelcontextprotocol.io)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Developer Guide](../../docs/DEVELOPER_GUIDE.md)
