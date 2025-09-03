# PIOPIY AI
Build Telephonic-Grade Voice AI — WebRTC-Ready Framework

Piopiy AI is an all-in-one platform for creating telephony-ready voice agents. Purchase numbers, configure agents, and let Piopiy handle call routing, audio streaming, and connectivity. The SDK plugs into your agent logic and supports many LLM, STT, and TTS providers so you can focus on conversation design.

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


async def create_session():
    voice_agent = VoiceAgent(
        instructions="You are an advanced voice AI.",
        greeting="Hello! How can I help you today?",
    )

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
    tts = CartesiaTTSService(api_key=os.getenv("CARTESIA_API_KEY"))

    await voice_agent.AgentAction(stt=stt, llm=llm, tts=tts)
    await voice_agent.start()


async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session,
    )
    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
```

## Providers

| Provider | STT | LLM | TTS | Memory | Other |
|---------|-----|-----|-----|--------|-------|
| [Anthropic](docs/llm/anthropic.md) |  | 😊 |  |  |  |
| [AssemblyAI](docs/stt/assemblyai.md) | 😊 |  |  |  |  |
| [AsyncAI](docs/tts/asyncai.md) |  |  | 😊 |  |  |
| [AWS](docs/llm/aws.md) | 😊 | 😊 | 😊 |  |  |
| [Azure](docs/llm/azure.md) | 😊 | 😊 | 😊 |  |  |
| [Cartesia](docs/stt/cartesia.md) | 😊 |  | 😊 |  |  |
| [Cerebras](docs/llm/cerebras.md) |  | 😊 |  |  |  |
| [Deepgram](docs/stt/deepgram.md) | 😊 |  | 😊 |  |  |
| [DeepSeek](docs/llm/deepseek.md) |  | 😊 |  |  |  |
| [ElevenLabs](docs/tts/elevenlabs.md) |  |  | 😊 |  |  |
| [Fal](docs/stt/fal.md) | 😊 |  |  |  |  |
| [Fireworks](docs/llm/fireworks.md) |  | 😊 |  |  |  |
| [Fish](docs/tts/fish.md) |  |  | 😊 |  |  |
| [Gladia](docs/stt/gladia.md) | 😊 |  |  |  |  |
| [Google](docs/llm/google.md) | 😊 | 😊 | 😊 |  |  |
| [Grok](docs/llm/grok.md) |  | 😊 |  |  |  |
| [Groq](docs/llm/groq.md) | 😊 | 😊 | 😊 |  |  |
| [Inworld](docs/tts/inworld.md) |  |  | 😊 |  |  |
| [LMNT](docs/tts/lmnt.md) |  |  | 😊 |  |  |
| [Mistral](docs/llm/mistral.md) |  | 😊 |  |  |  |
| [Minimax](docs/tts/minimax.md) |  |  | 😊 |  |  |
| [Neuphonic](docs/tts/neuphonic.md) |  |  | 😊 |  |  |
| [NIM](docs/llm/nim.md) |  | 😊 |  |  |  |
| [Ollama](docs/llm/ollama.md) |  | 😊 |  |  |  |
| [OpenAI](docs/llm/openai.md) | 😊 | 😊 | 😊 |  |  |
| [OpenPipe](docs/llm/openpipe.md) |  | 😊 |  |  |  |
| [OpenRouter](docs/llm/openrouter.md) |  | 😊 |  |  |  |
| [Perplexity](docs/llm/perplexity.md) |  | 😊 |  |  |  |
| [Piper](docs/tts/piper.md) |  |  | 😊 |  |  |
| [PlayHT](docs/tts/playht.md) |  |  | 😊 |  |  |
| [Qwen](docs/llm/qwen.md) |  | 😊 |  |  |  |
| [Rime](docs/tts/rime.md) |  |  | 😊 |  |  |
| [Riva](docs/stt/riva.md) | 😊 |  | 😊 |  |  |
| [SambaNova](docs/llm/sambanova.md) | 😊 | 😊 |  |  |  |
| [Sarvam](docs/tts/sarvam.md) |  |  | 😊 |  |  |
| [Soniox](docs/stt/soniox.md) | 😊 |  |  |  |  |
| [Speechmatics](docs/stt/speechmatics.md) | 😊 |  |  |  |  |
| [TeleCMI](docs/transport/telecmi.md) |  |  |  |  | 😊 |
| [Together](docs/llm/together.md) |  | 😊 |  |  |  |
| [Ultravox](docs/stt/ultravox.md) | 😊 |  |  |  |  |
| [Whisper](docs/stt/whisper.md) | 😊 |  |  |  |  |
| [XTTS](docs/tts/xtts.md) |  |  | 😊 |  |  |
| [Endor](docs/endor.md) | 😊 | 😊 | 😊 | 😊 | 😊 |

### Interruption & Silero VAD

Enable interruption handling with Silero voice activity detection:

```bash
pip install "piopiy-ai[silero]"
```

Silero VAD detects speech during playback, allowing callers to interrupt the agent.

## Telephony Integration

Connect phone calls in minutes using the Piopiy dashboard:

1. Sign in at [dashboard.piopiy.com](https://dashboard.piopiy.com) and purchase a phone number.
2. Create a voice AI agent to receive `AGENT_ID` and `AGENT_TOKEN`.
3. Use those credentials with the SDK for instant connectivity.

No SIP setup or third-party telephony vendors are required—Piopiy handles the calls so you can focus on your agent logic.

Thanks to Pepicat for making client SDK implementation easy.
