# Basic Voice Agent Example

This is the simplest example demonstrating a complete voice AI agent using Piopiy.

## What This Example Does

Creates a basic voice agent that:
- Listens to user speech (via Deepgram STT)
- Processes it with AI (via OpenAI LLM)
- Responds with natural voice (via Cartesia TTS)
- Supports interruptions (via Silero VAD)

## Installation

```bash
pip install "piopiy-ai[cartesia,deepgram,openai,silero]" python-dotenv
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

# Optional
AGENT_DEBUG=false  # Set to "true" for verbose logging
```

## Running the Example

```bash
python example/basic/basic.py
```

You should see:
```
🚀 Agent starting...
   Waiting for calls...
```

## Making a Test Call

1. Go to [dashboard.piopiy.com](https://dashboard.piopiy.com)
2. Navigate to your agent
3. Click "Test Call"
4. Enter your phone number
5. The agent will call you!

## How It Works

```python
# 1. Define what happens for each call
async def create_session(agent_id, call_id, from_number, to_number, metadata=None, **kwargs):
    # 2. Create voice agent with instructions
    voice_agent = VoiceAgent(
        instructions="You are a helpful AI assistant.",
        greeting="Hello! How can I help you today?",
    )
    
    # 3. Configure services
    stt = DeepgramSTTService(api_key=...)  # Speech-to-Text
    llm = OpenAILLMService(api_key=...)    # Language Model
    tts = CartesiaTTSService(api_key=...)  # Text-to-Speech
    
    # 4. Start the agent
    await voice_agent.Action(stt=stt, llm=llm, tts=tts, vad=True)
    await voice_agent.start()

# 5. Connect to Piopiy
agent = Agent(agent_id=..., agent_token=..., create_session=create_session)
await agent.connect()
```

## Customization

### Change the Voice

```python
tts = CartesiaTTSService(
    api_key=os.getenv("CARTESIA_API_KEY"),
    voice_id="a0e99841-438c-4a64-b679-ae501e7d6091"  # Different voice
)
```

### Change the AI Model

```python
llm = OpenAILLMService(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o"  # More powerful model
)
```

### Customize Instructions

```python
voice_agent = VoiceAgent(
    instructions="""You are a friendly customer service agent.
    - Be helpful and professional
    - Keep responses concise
    - Ask clarifying questions when needed""",
    greeting="Thank you for calling! How may I assist you today?",
)
```

## Next Steps

- **[MCP Sales Example](../mcp_sales/)** - Add function calling and tools
- **[Function Calling Examples](../function_calling/)** - Weather, CRM integrations
- **[Provider Switching](../switch_providers/)** - Dynamic provider changes
- **[Murf.ai TTS](../murf/)** - High-quality natural voices

## Troubleshooting

### Agent won't start
- Check `AGENT_ID` and `AGENT_TOKEN` are correct
- Verify internet connection

### No audio during call
- Verify all API keys are set
- Check provider accounts have credits
- Enable `AGENT_DEBUG=true` to see logs

### Import errors
- Reinstall: `pip install "piopiy-ai[cartesia,deepgram,openai,silero]" python-dotenv`
- Check Python version: `python --version` (requires 3.10+)

## Resources

- [Developer Guide](../../docs/DEVELOPER_GUIDE.md)
- [API Reference](../../docs/API_REFERENCE.md)
- [Main README](../../README.md)
