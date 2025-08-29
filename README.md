# PIOPIY AI
Build Telephonic-Grade Voice AI — WebRTC-Ready Framework

PIOPIY AI is an all-in-one platform for creating telephony-ready voice agents. Purchase numbers, configure agents, and let Piopiy handle call routing, audio streaming, and connectivity. The SDK plugs into your agent logic and supports many LLM, STT, and TTS providers so you can focus on conversation design.

## Installation

Requires Python 3.10+.

```bash
pip install piopiy-ai
```

### LLM Providers

Install optional extras for any language model providers you use.

Supported LLM providers:

- Anthropic
- AWS (Bedrock)
- Azure
- Cerebras
- DeepSeek
- Fireworks
- Google
- Grok
- Groq
- Mistral
- NIM
- Ollama
- OpenAI
- OpenPipe
- OpenRouter
- Perplexity
- Qwen
- Sambanova
- Together

Set provider API keys in the environment (for example, `OPENAI_API_KEY`).

### Speech-to-Text (STT)

Supported STT providers:

- AssemblyAI
- Azure
- AWS
- Cartesia
- Deepgram
- Fal
- Gladia
- Google
- Groq
- OpenAI
- Riva
- Sambanova
- Soniox
- Speechmatics
- Ultravox
- Whisper

Install the required extras and set their API keys (for example, `DEEPGRAM_API_KEY`).

### Text-to-Speech (TTS)

Supported TTS providers:

- AsyncAI
- AWS
- Azure
- Cartesia
- Deepgram
- ElevenLabs
- Fish
- Google
- Groq
- Inworld
- LMNT
- Minimax
- Neuphonic
- OpenAI
- Piper
- PlayHT
- Rime
- Riva
- Sarvam
- XTTS

Install the required extras and set their API keys (for example, `CARTESIA_API_KEY`).

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

