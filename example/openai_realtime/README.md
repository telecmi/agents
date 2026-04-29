# OpenAI Realtime — Speech-to-Speech Agent

Speech-to-speech voice agent using OpenAI's Realtime API (`gpt-realtime` /
`gpt-4o-realtime-preview`). The model takes user audio in and emits agent
audio out — no separate STT or TTS stage.

See [docs/REALTIME_MODELS.md](../../docs/REALTIME_MODELS.md#2-openai-realtime)
for the full constructor reference.

## Install

```bash
pip install "piopiy-ai[openai,silero]" python-dotenv
```

## Environment

```bash
AGENT_ID=...
AGENT_TOKEN=...
OPENAI_API_KEY=...
```

## Run

```bash
python example/openai_realtime/openai_realtime_agent.py
```

## Voices

OpenAI Realtime ships with: `alloy`, `echo`, `fable`, `onyx`, `nova`,
`shimmer`, `coral`, `verse`. Set via
`session_properties=events.SessionProperties(voice="...")`.

## Function calling

Add tools the same way as cascaded mode:

```python
from piopiy.adapters.schemas.function_schema import FunctionSchema

async def get_weather(location: str):
    return {"temp": 72, "condition": "sunny"}

schema = FunctionSchema(
    name="get_weather",
    description="Get weather for a location",
    properties={"location": {"type": "string"}},
    required=["location"],
)
voice_agent.add_tool(schema, get_weather)
```

## Other realtime models

- [Gemini Live](../gemini_live/) (Google)
- [AWS Nova Sonic](../aws_nova_sonic/)
- [Azure OpenAI Realtime](../azure_realtime/)
- [Grok Realtime](../grok_realtime/) (xAI)
