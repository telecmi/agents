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

| Provider | Categories |
|---------|------------|
| [Anthropic](docs/llm/anthropic.md) | LLM |
| [AssemblyAI](docs/stt/assemblyai.md) | STT |
| [AsyncAI](docs/tts/asyncai.md) | TTS |
| [AWS](docs/llm/aws.md) | LLM, STT, TTS |
| [Azure](docs/llm/azure.md) | LLM, STT, TTS |
| [Cartesia](docs/stt/cartesia.md) | STT, TTS |
| [Cerebras](docs/llm/cerebras.md) | LLM |
| [Deepgram](docs/stt/deepgram.md) | STT, TTS |
| [DeepSeek](docs/llm/deepseek.md) | LLM |
| [ElevenLabs](docs/tts/elevenlabs.md) | TTS |
| [Fal](docs/stt/fal.md) | STT |
| [Fireworks](docs/llm/fireworks.md) | LLM |
| [Fish](docs/tts/fish.md) | TTS |
| [Gladia](docs/stt/gladia.md) | STT |
| [Google](docs/llm/google.md) | LLM, STT, TTS |
| [Grok](docs/llm/grok.md) | LLM |
| [Groq](docs/llm/groq.md) | LLM, STT, TTS |
| [Inworld](docs/tts/inworld.md) | TTS |
| [LMNT](docs/tts/lmnt.md) | TTS |
| [Mistral](docs/llm/mistral.md) | LLM |
| [Minimax](docs/tts/minimax.md) | TTS |
| [Neuphonic](docs/tts/neuphonic.md) | TTS |
| [NIM](docs/llm/nim.md) | LLM |
| [Ollama](docs/llm/ollama.md) | LLM |
| [OpenAI](docs/llm/openai.md) | LLM, STT, TTS |
| [OpenPipe](docs/llm/openpipe.md) | LLM |
| [OpenRouter](docs/llm/openrouter.md) | LLM |
| [Perplexity](docs/llm/perplexity.md) | LLM |
| [Piper](docs/tts/piper.md) | TTS |
| [PlayHT](docs/tts/playht.md) | TTS |
| [Qwen](docs/llm/qwen.md) | LLM |
| [Rime](docs/tts/rime.md) | TTS |
| [Riva](docs/stt/riva.md) | STT, TTS |
| [SambaNova](docs/llm/sambanova.md) | LLM, STT |
| [Sarvam](docs/tts/sarvam.md) | TTS |
| [Soniox](docs/stt/soniox.md) | STT |
| [Speechmatics](docs/stt/speechmatics.md) | STT |
| [TeleCMI](docs/transport/telecmi.md) | Transport |
| [Together](docs/llm/together.md) | LLM |
| [Ultravox](docs/stt/ultravox.md) | STT |
| [Whisper](docs/stt/whisper.md) | STT |
| [XTTS](docs/tts/xtts.md) | TTS |

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
