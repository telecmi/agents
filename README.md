# PIOPIY AI
Build Telephonic-Grade Voice AI — WebRTC-Ready Framework


Piopiy AI is an all-in-one platform for creating telephony-ready voice agents. Purchase numbers, configure agents, and let Piopiy handle call routing, audio streaming, and connectivity. The SDK plugs into your agent logic and supports many LLM, STT, and TTS providers so you can focus on conversation design.


## Installation

Requires Python 3.10+.

```bash
pip install piopiy-ai
```

### LLM Providers

Install optional extras for any language model providers you use.

Supported LLM providers:


- [Anthropic](docs/llm/anthropic.md)
- [AWS (Bedrock)](docs/llm/aws.md)
- [Azure](docs/llm/azure.md)
- [Cerebras](docs/llm/cerebras.md)
- [DeepSeek](docs/llm/deepseek.md)
- [Fireworks](docs/llm/fireworks.md)
- [Google](docs/llm/google.md)
- [Grok](docs/llm/grok.md)
- [Groq](docs/llm/groq.md)
- [Mistral](docs/llm/mistral.md)
- [NIM](docs/llm/nim.md)
- [Ollama](docs/llm/ollama.md)
- [OpenAI](docs/llm/openai.md)
- [OpenPipe](docs/llm/openpipe.md)
- [OpenRouter](docs/llm/openrouter.md)
- [Perplexity](docs/llm/perplexity.md)
- [Qwen](docs/llm/qwen.md)
- [SambaNova](docs/llm/sambanova.md)
- [Together](docs/llm/together.md)


Set provider API keys in the environment (for example, `OPENAI_API_KEY`).

### Speech-to-Text (STT)

Supported STT providers:


- [AssemblyAI](docs/stt/assemblyai.md)
- [Azure](docs/stt/azure.md)
- [AWS](docs/stt/aws.md)
- [Cartesia](docs/stt/cartesia.md)
- [Deepgram](docs/stt/deepgram.md)
- [Fal](docs/stt/fal.md)
- [Gladia](docs/stt/gladia.md)
- [Google](docs/stt/google.md)
- [Groq](docs/stt/groq.md)
- [OpenAI](docs/stt/openai.md)
- [Riva](docs/stt/riva.md)
- [SambaNova](docs/stt/sambanova.md)
- [Soniox](docs/stt/soniox.md)
- [Speechmatics](docs/stt/speechmatics.md)
- [Ultravox](docs/stt/ultravox.md)
- [Whisper](docs/stt/whisper.md)


Install the required extras and set their API keys (for example, `DEEPGRAM_API_KEY`).

### Text-to-Speech (TTS)

Supported TTS providers:

- [AsyncAI](docs/tts/asyncai.md)
- [AWS](docs/tts/aws.md)
- [Azure](docs/tts/azure.md)
- [Cartesia](docs/tts/cartesia.md)
- [Deepgram](docs/tts/deepgram.md)
- [ElevenLabs](docs/tts/elevenlabs.md)
- [Fish](docs/tts/fish.md)
- [Google](docs/tts/google.md)
- [Groq](docs/tts/groq.md)
- [Inworld](docs/tts/inworld.md)
- [LMNT](docs/tts/lmnt.md)
- [Minimax](docs/tts/minimax.md)
- [Neuphonic](docs/tts/neuphonic.md)
- [OpenAI](docs/tts/openai.md)
- [Piper](docs/tts/piper.md)
- [PlayHT](docs/tts/playht.md)
- [Rime](docs/tts/rime.md)
- [Riva](docs/tts/riva.md)
- [Sarvam](docs/tts/sarvam.md)
- [XTTS](docs/tts/xtts.md)

Install the required extras and set their API keys (for example, `CARTESIA_API_KEY`).

### Transports

Supported transports:


- [TeleCMI](docs/transport/telecmi.md)



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

