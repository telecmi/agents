# Open-Source Voice Agent Examples

Two reference stacks running fully on local / self-hosted models. Same
`VoiceAgent.configure()` API as the cloud examples — only the services change.

## What's here

| File | Mode | Stack | When to use |
|---|---|---|---|
| [`cascaded.py`](cascaded.py) | Cascaded (STT → LLM → TTS) | Whisper + Ollama + Chatterbox | Maximum control: swap each stage independently. Best when you want a specific TTS voice or domain-tuned STT vocabulary. |
| [`hybrid.py`](hybrid.py) | Audio-LLM hybrid (audio-in LLM → external TTS) | Ultravox + VibeVoice | Lower latency than cascaded — Ultravox replaces STT+LLM in one model. Pair with any TTS for the agent's voice. |

For comparison: `example/gemini_live/gemini_live_agent.py` shows pure
**speech-to-speech** mode (the model owns audio in *and* out — no STT, no
TTS). Gemini Live is cloud, but the same pattern works for any S2S model
including a self-hosted one (see
[docs/CUSTOM_SERVICES.md](../../docs/CUSTOM_SERVICES.md#4-custom-realtime--speech-to-speech)).

## All three open-source modes at a glance

```python
# 1. Cascaded — independent open-source services
await voice_agent.configure(
    stt=WhisperSTTService(model="small"),
    llm=OLLamaLLMService(model="llama3.1"),
    tts=ChatterboxTTSService(base_url="ws://localhost:6078"),
    vad=True,
)

# 2. Audio-LLM hybrid — model does ASR+LLM, external TTS
await voice_agent.configure(
    llm=UltravoxService(server_url="ws://localhost:8766"),
    tts=OpenVibeVoiceTTSService(server_url="ws://localhost:8765"),
    vad=SileroVADAnalyzer(),
)

# 3. Speech-to-speech — model handles audio both ways (no stt, no tts)
await voice_agent.configure(llm=my_self_hosted_realtime_model)
```

## Setup

### Cascaded stack (`cascaded.py`)

```bash
pip install "piopiy-ai[whisper,silero]" python-dotenv
```

Start the runtimes:

1. **Ollama** — https://ollama.ai
   ```bash
   ollama pull llama3.1
   ollama serve  # runs at http://localhost:11434
   ```

2. **Chatterbox TTS** — https://github.com/piopiy-ai/chatterbox-tts
   ```bash
   # Follow the project's README to start the WebSocket server on port 6078.
   ```

Whisper runs in-process (no separate server needed).

`.env`:
```bash
AGENT_ID=your_agent_id
AGENT_TOKEN=your_agent_token
OLLAMA_MODEL=llama3.1                       # optional
OLLAMA_BASE_URL=http://localhost:11434      # optional
CHATTERBOX_BASE_URL=ws://localhost:6078     # optional
```

Run:
```bash
python example/opensource/cascaded.py
```

### Hybrid stack (`hybrid.py`)

```bash
pip install piopiy-ai python-dotenv
```

Start the runtimes:

1. **Ultravox** — your self-hosted Ultravox server (default port 8766)
2. **VibeVoice** — your self-hosted VibeVoice server (default port 8765)

`.env`:
```bash
AGENT_ID=your_agent_id
AGENT_TOKEN=your_agent_token
ULTRAVOX_SERVER_URL=ws://localhost:8766     # optional
VIBEVOICE_SERVER_URL=ws://localhost:8765    # optional
```

Run:
```bash
python example/opensource/hybrid.py
```

## Mixing open-source and cloud

`configure()` does not care whether each service is cloud or local. Mix
freely based on cost, latency, and privacy goals:

```python
# Cheap STT on the device, premium cloud LLM, premium cloud TTS
await voice_agent.configure(
    stt=WhisperSTTService(model="small"),
    llm=OpenAILLMService(api_key=..., model="gpt-4o-mini"),
    tts=CartesiaTTSService(api_key=...),
    vad=True,
)
```

## Adding your own open-source model

If your model isn't listed in [docs/PROVIDERS.md](../../docs/PROVIDERS.md),
write a custom service — see
[docs/CUSTOM_SERVICES.md](../../docs/CUSTOM_SERVICES.md) for templates of all
four shapes (STT, audio-LLM, S2S, TTS).

Once you've subclassed the right base class, plug your service into
`configure()` exactly like any of the bundled providers.

## See also

- [docs/CUSTOM_SERVICES.md](../../docs/CUSTOM_SERVICES.md) — write your own service
- [docs/MIGRATION.md](../../docs/MIGRATION.md) — moving older code to the unified API
- [docs/DEVELOPER_GUIDE.md](../../docs/DEVELOPER_GUIDE.md#cascaded-vs-speech-to-speech) — cascaded vs S2S concepts
- [example/chatterbox/](../chatterbox/) — Chatterbox-only example
- [example/gemini_live/](../gemini_live/) — speech-to-speech reference
- [example/ultravox/](../ultravox/) — Ultravox examples (also hybrid mode)
