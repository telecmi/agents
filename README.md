# PIOPIY AI
Build Telephonic-Grade Voice AI — WebRTC-Ready Framework

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


async def create_session():
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

