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

`VoiceAgent` works in two modes — **cascaded** (separate STT, LLM, TTS) and
**speech-to-speech** (a single realtime model owns audio I/O). Both use the
same `configure()` API; the mode is selected by what you pass.

### Cascaded mode

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
    """Called for each incoming call."""
    print(f"📞 Incoming call {call_id} from {from_number} to {to_number}")
    if metadata:
        print(f"   Metadata: {metadata}")

    voice_agent = VoiceAgent(
        instructions="You are a helpful AI assistant. Be concise and friendly.",
        greeting="Hello! How can I help you today?",
    )

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="bdab08ad-4137-4548-b9db-6142854c7525",
    )

    await voice_agent.configure(
        stt=stt,
        llm=llm,
        tts=tts,
        vad=True,
        allow_interruptions=True,
    )
    await voice_agent.start()


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
        debug=False,
    )
    print("🚀 Agent starting... waiting for calls.")
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
```

### Speech-to-speech mode

For realtime models like Gemini Live or OpenAI Realtime, drop STT and TTS — the
model consumes user audio and emits agent audio directly:

```python
from piopiy.services.google.gemini_live.llm import (
    GeminiLiveLLMService, GeminiModalities, InputParams,
)

async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    voice_agent = VoiceAgent(
        instructions="You are a friendly voice assistant.",
        greeting="Hi! How can I help?",
    )

    llm = GeminiLiveLLMService(
        api_key=os.getenv("GOOGLE_API_KEY"),
        model="models/gemini-2.0-flash-exp",
        params=InputParams(modalities=GeminiModalities.AUDIO),
    )

    await voice_agent.configure(llm=llm, allow_interruptions=True)
    await voice_agent.start()
```

Same `VoiceAgent`, same `configure()`, same `start()`. The presence or absence
of `tts=` is what selects the mode.

> **Compatibility:** older code using `voice_agent.Action(...)` or the
> separate `SpeechAgent` class still works — both forward to
> `VoiceAgent.configure()`. New code should prefer `configure()`.

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

**Cascaded mode** (STT → LLM → TTS):

1. **Incoming Call**: Your `create_session` function is invoked
2. **Greeting**: The agent speaks the greeting via the TTS service
3. **Listening**: STT converts user speech to text
4. **Processing**: LLM generates a text response
5. **Speaking**: TTS converts the text to audio
6. **Loop**: Steps 3–5 continue until the call ends

**Speech-to-speech mode** (realtime model):

1. **Incoming Call**: `create_session` is invoked
2. **Greeting**: The realtime model speaks the greeting (set in the context)
3. **Conversation**: User audio streams in; agent audio streams out — the model handles both
4. **Loop**: Continues until the call ends

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
