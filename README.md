# PIOPIY AI
[![PyPI](https://img.shields.io/pypi/v/piopiy-ai)](https://pypi.org/project/piopiy-ai/)
[![Python](https://img.shields.io/pypi/pyversions/piopiy-ai)](https://pypi.org/project/piopiy-ai/)
[![License](https://img.shields.io/pypi/l/piopiy-ai)](https://github.com/telecmi/agents/blob/main/LICENSE)

**Telephonic-Grade Voice AI — WebRTC-Ready Framework**

Piopiy AI is an open-source, telephony-grade framework for building real-time voice agents that blend large language models (LLM), automatic speech recognition (ASR), and text-to-speech (TTS) engines. Purchase numbers, configure agents, and let Piopiy handle call routing, audio streaming, and connectivity while you focus on conversation design. Combine cloud or open-source providers to tailor the voice stack to your latency, privacy, and cost targets.

## Installation

Requires Python 3.10+.

```bash
pip install piopiy-ai
```

To install extras for the providers you plan to use:

```bash
pip install "piopiy-ai[cartesia,deepgram,openai]"
```

Set provider API keys in the environment (for example, `OPENAI_API_KEY`).

## Quick Example

```python
import asyncio
import os

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.cartesia.tts import CartesiaTTSService


async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    print(f"Incoming call {call_id} from {from_number} to {to_number}")
    if metadata:
        print(f"Call Metadata: {metadata}")

    voice_agent = VoiceAgent(
        instructions="You are an advanced voice AI.",
        greeting="Hello! How can I help you today?",
    )

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
    tts = CartesiaTTSService(api_key=os.getenv("CARTESIA_API_KEY"))

    await voice_agent.Action(stt=stt, llm=llm, tts=tts)
    await voice_agent.start()


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
        debug=True # Enable debug logging (optional, default: False)
    )
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration & Debugging

### Debug Mode

You can control the verbosity of the logs using the `debug` parameter in the `Agent` constructor.

-   **`debug=True`**: Enables INFO level logging and prints full debug information, including internal events and third-party provider logs (e.g., Deepgram, Websockets). Useful during development.
-   **`debug=False`** (Default): Sets logging to ERROR level and suppresses noisy third-party logs. This keeps your console clean and focuses on your application's output (like metadata).

### Handling Metadata

The `create_session` function receives `metadata` as a dictionary if it was passed when initiating the call.

-   **Automatic Parsing**: Piopiy automatically parses JSON metadata strings into Python dictionaries.
-   **Key-Value Access**: You can access properties directly, e.g., `metadata.get('customer_name')`.

```python
async def create_session(agent_id, call_id, metadata=None, **kwargs):
    if metadata:
        customer_id = metadata.get("customer_id")
        print(f"Handling call for customer: {customer_id}")
```

## 📚 Documentation

### Quick Links

- **[Getting Started](docs/GETTING_STARTED.md)** - Installation, setup, and your first voice agent
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Core concepts, building agents, and advanced features
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[Telephony Setup](docs/TELEPHONY.md)** - Phone numbers, deployment, and production best practices
- **[Supported Providers](docs/PROVIDERS.md)** - 40+ LLM, STT, and TTS providers
- **[Examples](example/README.md)** - Code examples and use cases

### Learning Path

1. **New to Piopiy?** Start with [Getting Started](docs/GETTING_STARTED.md)
2. **Building your agent?** Read the [Developer Guide](docs/DEVELOPER_GUIDE.md)
3. **Need API details?** Check the [API Reference](docs/API_REFERENCE.md)
4. **Deploying to production?** Follow [Telephony Setup](docs/TELEPHONY.md)

## Advanced Usage & Dynamic Switching

Piopiy AI supports advanced features like switching providers mid-call (e.g., swapping TTS voices or STT models based on user commands).

Check out the [Switching Providers Examples](example/switch_providers/README.md) to see how to implement dynamic provider switching with `ServiceSwitcher`.

## Supported Providers

Piopiy AI supports 40+ providers. Here are some of the most popular ones:

- **LLM**: OpenAI, Anthropic, Google Gemini, Groq, unsloth (via Ollama)
- **STT**: Deepgram, Speechmatics, Google, Azure, AssemblyAI, Whisper
- **TTS**: ElevenLabs, Cartesia, PlayHT, Azure, Google, Rime

👉 **[See the full list of Supported Providers](docs/PROVIDERS.md)**

### Interruption & Silero VAD

Enable interruption handling with Silero voice activity detection:

```bash
pip install "piopiy-ai[silero]"
```

Silero VAD detects speech during playback, allowing callers to interrupt the agent.

## Open-Source Voice Stack (LLM + ASR + TTS)

Pair Piopiy’s realtime orchestration with open-source engines across the full speech stack:

| Layer | Default | Alternatives |
|-------|---------|--------------|
| **LLM** | [Ollama](https://ollama.ai) running `llama3.1` (or another local model) | [LM Studio](https://lmstudio.ai), [GPT4All](https://gpt4all.io) via Ollama-compatible APIs |
| **ASR** | `WhisperSTTService` with Whisper small/medium models | [`mlx-whisper`](https://github.com/ml-explore/mlx-examples/tree/main/whisper) for Apple silicon |
| **TTS** | `ChatterboxTTSService` pointed at a self-hosted [Chatterbox TTS](https://github.com/piopiy-ai/chatterbox-tts) server | Piper, XTTS, Kokoro |

Install the optional dependencies and runtimes:

```bash
pip install "piopiy-ai[whisper]"
# Install and run Ollama separately: https://ollama.ai
# Start the Chatterbox TTS WebSocket server (https://github.com/piopiy-ai/chatterbox-tts)
```

Example session factory using the open-source trio:

```python
from piopiy.voice_agent import VoiceAgent
from piopiy.services.whisper.stt import WhisperSTTService
from piopiy.services.ollama.llm import OLLamaLLMService
from piopiy.services.opensource.chatterbox.tts import ChatterboxTTSService


async def create_session():
    voice_agent = VoiceAgent(
        instructions="You are a helpful local-first voice assistant.",
        greeting="Hi there! Running fully on open-source models today.",
    )

    stt = WhisperSTTService(model="small")
    llm = OLLamaLLMService(model="llama3.1")  # points to your local Ollama runtime
    tts = ChatterboxTTSService(base_url="ws://localhost:6078")

    await voice_agent.Action(stt=stt, llm=llm, tts=tts, vad=True)
    await voice_agent.start()
```

Swap in other open-source providers such as Piper, XTTS, or Kokoro for TTS, and adjust the Chatterbox base URL or voice ID for your deployment. You can also run Whisper on Apple silicon with the `mlx-whisper` extra. Piopiy's abstraction layer lets you mix these with managed services whenever needed.

## Telephony Integration

Connect phone calls in minutes using the Piopiy dashboard:

1. Sign in at [dashboard.piopiy.com](https://dashboard.piopiy.com) and purchase a phone number.
2. Create a voice AI agent to receive `AGENT_ID` and `AGENT_TOKEN`.
3. Use those credentials with the SDK for instant connectivity.

No SIP setup or third-party telephony vendors are required—Piopiy handles the calls so you can focus on your agent logic.

Thanks to Pipecat for making client SDK implementation easy.

