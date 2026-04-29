# Grok Realtime — Speech-to-Speech Agent

Speech-to-speech voice agent using xAI's Grok Realtime API. Bidirectional
audio over WebSocket with built-in tools (web_search, x_search, file_search)
plus custom function calling.

See [docs/REALTIME_MODELS.md](../../docs/REALTIME_MODELS.md#5-grok-realtime-xai)
for the full constructor reference.

## Install

```bash
pip install "piopiy-ai[grok,silero]" python-dotenv
```

## Environment

```bash
AGENT_ID=...
AGENT_TOKEN=...
XAI_API_KEY=...
```

## Run

```bash
python example/grok_realtime/grok_realtime_agent.py
```

## Voices

`Ara`, `Rex`, `Sal`, `Eve`, `Leo`. Configure via
`session_properties=events.SessionProperties(voice="...")`.

## Audio formats

PCM, PCMU, PCMA at 8 kHz – 48 kHz. Configure via `session_properties`.

## Other realtime models

- [Gemini Live](../gemini_live/), [OpenAI Realtime](../openai_realtime/),
  [Azure OpenAI Realtime](../azure_realtime/), [AWS Nova Sonic](../aws_nova_sonic/)
