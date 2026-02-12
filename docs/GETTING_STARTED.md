# Getting Started with Piopiy AI

This guide will help you build your first telephony-grade voice AI agent in minutes.

## Prerequisites

- **Python 3.10+** installed
- **Piopiy Account**: Sign up at [dashboard.piopiy.com](https://dashboard.piopiy.com)
- **API Keys**: Get credentials from your chosen providers (OpenAI, Deepgram, Cartesia, etc.)

## Installation

### Basic Installation

```bash
pip install piopiy-ai
```

### Install with Provider Extras

For a quick start with popular cloud providers:

```bash
pip install "piopiy-ai[cartesia,deepgram,openai,silero]"
```

Available extras:
- `cartesia` - Cartesia TTS
- `deepgram` - Deepgram STT
- `openai` - OpenAI LLM
- `silero` - Silero VAD for interruption handling
- `whisper` - Whisper STT (open-source)
- `anthropic` - Anthropic Claude LLM
- `elevenlabs` - ElevenLabs TTS

See [PROVIDERS.md](PROVIDERS.md) for the complete list.

## Get Your Agent Credentials

1. Go to [dashboard.piopiy.com](https://dashboard.piopiy.com)
2. Navigate to **Voice AI Agents**
3. Click **Create Agent**
4. Copy your `AGENT_ID` and `AGENT_TOKEN`

## Environment Setup

Create a `.env` file in your project directory:

```bash
# Piopiy Credentials (required)
AGENT_ID=your_agent_id
AGENT_TOKEN=your_agent_token

# Provider API Keys
OPENAI_API_KEY=your_openai_key
DEEPGRAM_API_KEY=your_deepgram_key
CARTESIA_API_KEY=your_cartesia_key

# Optional: Enable debug logging
AGENT_DEBUG=false
```

## Your First Voice Agent

Create a file `my_agent.py`:

```python
import asyncio
import os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.cartesia.tts import CartesiaTTSService

load_dotenv()


async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    """
    This function is called for each incoming call.
    Build your voice agent logic here.
    """
    print(f"📞 Incoming call {call_id}")
    print(f"   From: {from_number}")
    print(f"   To: {to_number}")
    
    if metadata:
        print(f"   Metadata: {metadata}")

    # Create the voice agent
    voice_agent = VoiceAgent(
        instructions="You are a helpful AI assistant. Be concise and friendly.",
        greeting="Hello! How can I help you today?",
    )

    # Configure services
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="bdab08ad-4137-4548-b9db-6142854c7525"  # Default voice
    )

    # Start the agent
    await voice_agent.Action(
        stt=stt,
        llm=llm,
        tts=tts,
        vad=True,  # Enable voice activity detection
        allow_interruptions=True  # Allow user to interrupt
    )
    await voice_agent.start()


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
        debug=False  # Set to True for verbose logging
    )
    
    print("🚀 Agent starting...")
    print("   Waiting for calls...")
    
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
```

## Run Your Agent

```bash
python my_agent.py
```

You should see:
```
🚀 Agent starting...
   Waiting for calls...
```

## Make a Test Call

### Option 1: From Piopiy Dashboard

1. Go to your agent in the dashboard
2. Click **Test Call**
3. Enter your phone number
4. Click **Call**

### Option 2: Configure a Phone Number

1. Purchase a phone number in the dashboard
2. Assign it to your agent
3. Call the number from any phone

## What Happens During a Call

1. **Incoming Call**: Your `create_session` function is invoked
2. **Greeting**: The agent speaks the greeting message
3. **Listening**: STT converts speech to text
4. **Processing**: LLM generates a response
5. **Speaking**: TTS converts text to speech
6. **Loop**: Continues until call ends

## Understanding the Output

With `debug=False` (default), you'll see clean output:
```
📞 Incoming call 691cc791-7cb3-4251-9850-fb324f7ce0aa
   From: +1234567890
   To: +1987654321
   Metadata: {'customer_id': 'CUST_1001', 'campaign': 'summer_sale'}
```

With `debug=True`, you'll see detailed logs from all services.

## Next Steps

- **[Developer Guide](DEVELOPER_GUIDE.md)** - Learn core concepts and advanced features
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Examples](../example/README.md)** - More example agents
- **[Providers](PROVIDERS.md)** - Explore 40+ supported providers
- **[Telephony Setup](TELEPHONY.md)** - Production deployment guide

## Troubleshooting

### Agent won't start
- Verify `AGENT_ID` and `AGENT_TOKEN` are correct
- Check your internet connection
- Ensure Python 3.10+ is installed

### No audio during call
- Verify provider API keys are set
- Check provider account has credits
- Enable `debug=True` to see detailed logs

### Import errors
- Reinstall with extras: `pip install "piopiy-ai[provider_name]"`
- Check Python version: `python --version`

### Call connects but agent doesn't respond
- Check LLM API key and quota
- Verify STT service is configured correctly
- Review logs with `debug=True`

## Getting Help

- **Documentation**: [GitHub Repository](https://github.com/telecmi/agents)
- **Issues**: [Report bugs](https://github.com/telecmi/agents/issues)
- **Support**: Contact support@piopiy.com
