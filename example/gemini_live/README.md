# Gemini Live — Speech-to-Speech Voice Agent

A complete speech-to-speech voice agent using Google's Gemini Live realtime
multimodal model. The model consumes user audio and emits agent audio
directly — there is no separate STT or TTS stage.

This is the canonical example of speech-to-speech mode in Piopiy AI.

## Why speech-to-speech?

- **Lowest latency.** No STT round-trip, no TTS synthesis. Audio flows
  through a single model.
- **Natural prosody.** The model preserves emotion and tone in the user's
  audio when generating responses.
- **Simpler pipeline.** One service instead of three.

Trade-offs vs cascaded mode: limited control over voice timbre (you choose
from the model's voices), provider lock-in, and context length is limited by
the realtime model's session.

## Requirements

```bash
pip install "piopiy-ai[google,silero]" python-dotenv
```

## Environment

```bash
AGENT_ID=...
AGENT_TOKEN=...
GOOGLE_API_KEY=...
```

## Run

```bash
python example/gemini_live/gemini_live_agent.py
```

## How the pipeline differs from cascaded mode

```python
# Cascaded — three separate services:
await voice_agent.configure(stt=deepgram, llm=openai, tts=cartesia)

# Speech-to-speech — one service handles both ends:
await voice_agent.configure(llm=gemini_live)
```

The `VoiceAgent` auto-detects the mode from the arguments. With no `stt` or
`tts`, it builds a `transport.input → llm → transport.output` pipeline and
queues an `LLMRunFrame()` so the model produces the greeting from the system
context.

## Other realtime models

The same pattern works for any speech-to-speech LLM:

- `OpenAIRealtimeLLMService` (OpenAI Realtime)
- `AWSNovaSonicLLMService` (Amazon Nova Sonic)
- `GrokLiveLLMService` (xAI Grok Realtime)
- `AzureRealtimeLLMService` (Azure OpenAI Realtime)

## Migrating from `SpeechAgent` + `PassThroughTTS`

Older code that used a `PassThroughTTS` shim with `SpeechAgent`:

```python
# old
agent = SpeechAgent(instructions=..., greeting=...)
await agent.Action(omni=gemini_live, tts=PassThroughTTS(), vad=True)
```

becomes simply:

```python
# new
voice_agent = VoiceAgent(instructions=..., greeting=...)
await voice_agent.configure(llm=gemini_live, vad=True)
```

The old form still works (`SpeechAgent` is a thin shim around `VoiceAgent`
and silently drops the `PassThroughTTS` dummy), but new code should use
`VoiceAgent.configure()` directly.
