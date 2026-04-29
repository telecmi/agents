# Realtime / Speech-to-Speech Models

This page lists every realtime model Piopiy supports, with full constructor
signatures and a copy-paste example for each. All of these run through
`VoiceAgent.configure(llm=..., ...)` — pure speech-to-speech mode if you pass
no `tts`, audio-LLM hybrid mode if you also pass a `tts=`.

## Inventory

| Model | Class | Mode | Import |
|---|---|---|---|
| **Gemini Live** (Google) | `GeminiLiveLLMService` | S2S | `piopiy.services.google.gemini_live.llm` |
| **OpenAI Realtime** | `OpenAIRealtimeLLMService` | S2S | `piopiy.services.openai.realtime.llm` |
| **OpenAI Realtime Beta** *(legacy)* | `OpenAIRealtimeBetaLLMService` | S2S | `piopiy.services.openai_realtime_beta.openai` |
| **Azure OpenAI Realtime** | `AzureRealtimeLLMService` | S2S | `piopiy.services.azure.realtime.llm` |
| **AWS Nova Sonic** | `AWSNovaSonicLLMService` | S2S | `piopiy.services.aws.nova_sonic.llm` |
| **Grok Realtime** (xAI) | `GrokRealtimeLLMService` | S2S | `piopiy.services.grok.realtime.llm` |
| **Ultravox Realtime** (cloud) | `UltravoxRealtimeLLMService` | Audio-LLM hybrid | `piopiy.services.ultravox.llm` |
| **Ultravox** (open-source) | `UltravoxService` | Audio-LLM hybrid | `piopiy.services.opensource.ultravox.omni` |

> **Mode legend** — **S2S**: model consumes user audio and emits agent audio
> directly. Use with no `stt=` and no `tts=`. **Audio-LLM hybrid**: model
> consumes user audio but emits text; pair with a TTS service for output.

## Common pipeline shape

For every S2S model below the call site is the same:

```python
voice_agent = VoiceAgent(instructions="...", greeting="...")
await voice_agent.configure(llm=<service>, allow_interruptions=True)
await voice_agent.start()
```

For audio-LLM hybrids (Ultravox), add `tts=<some_tts_service>`.

---

## 1. Gemini Live (Google)

**Class:** `GeminiLiveLLMService`
**Modalities:** audio + text + video (input), audio + text (output)
**Function calling:** ✅ Yes
**Server-side VAD:** ✅ On by default

### Constructor parameters

```python
GeminiLiveLLMService(
    *,
    api_key: str,                                           # Google AI API key
    model: str = "models/gemini-2.5-flash-native-audio-preview-12-2025",
    voice_id: str = "Charon",                               # Aoede, Charon, Fenrir, Kore, Puck
    start_audio_paused: bool = False,
    start_video_paused: bool = False,
    system_instruction: Optional[str] = None,
    tools: Optional[Union[List[dict], ToolsSchema]] = None,
    params: Optional[InputParams] = None,                   # modalities, temperature, language, etc.
    inference_on_context_initialization: bool = True,
    file_api_base_url: str = "https://generativelanguage.googleapis.com/v1beta/files",
    http_options: Optional[HttpOptions] = None,
)
```

`InputParams` (from same module):
- `modalities: GeminiModalities` — `AUDIO`, `TEXT`, etc.
- `temperature: float` — sampling temperature
- `language: Language` — caller language
- `media_resolution`, `vad`, `context_window_compression`

### Example

```python
import asyncio, os
from dotenv import load_dotenv

from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent
from piopiy.services.google.gemini_live.llm import (
    GeminiLiveLLMService, GeminiModalities, InputParams,
)

load_dotenv()

async def create_session(call_id, from_number, to_number, metadata=None, **_):
    voice_agent = VoiceAgent(
        instructions="You are a friendly voice assistant.",
        greeting="Hi! This is Gemini Live. How can I help?",
    )

    llm = GeminiLiveLLMService(
        api_key=os.getenv("GOOGLE_API_KEY"),
        model="models/gemini-2.0-flash-exp",
        voice_id="Aoede",
        params=InputParams(
            modalities=GeminiModalities.AUDIO,
            temperature=0.7,
        ),
    )

    await voice_agent.configure(llm=llm, allow_interruptions=True)
    await voice_agent.start()

asyncio.run(Agent(
    agent_id=os.getenv("AGENT_ID"),
    agent_token=os.getenv("AGENT_TOKEN"),
    create_session=create_session,
).connect())
```

Install: `pip install "piopiy-ai[google,silero]"` · Env: `GOOGLE_API_KEY`

---

## 2. OpenAI Realtime

**Class:** `OpenAIRealtimeLLMService`
**Modalities:** audio + text + video (input), audio + text (output)
**Function calling:** ✅ Yes
**Server-side VAD:** ✅ On by default (configurable in `session_properties`)

### Constructor parameters

```python
OpenAIRealtimeLLMService(
    *,
    api_key: str,                                           # OpenAI API key
    model: str = "gpt-realtime",
    base_url: str = "wss://api.openai.com/v1/realtime",
    session_properties: Optional[SessionProperties] = None, # voice, modalities, turn_detection, etc.
    start_audio_paused: bool = False,
    start_video_paused: bool = False,
    video_frame_detail: str = "auto",                       # "auto" | "low" | "high"
)
```

`SessionProperties` (from `piopiy.services.openai.realtime.events`):
- `voice: str` — `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`, `coral`, `verse`
- `modalities: List[str]` — `["audio", "text"]`
- `instructions: str` — system prompt (overridable per session)
- `turn_detection: TurnDetection` — server-side VAD config
- `temperature`, `max_response_output_tokens`, `tool_choice`

### Example

```python
from piopiy.services.openai.realtime.llm import OpenAIRealtimeLLMService
from piopiy.services.openai.realtime import events

llm = OpenAIRealtimeLLMService(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-realtime",
    session_properties=events.SessionProperties(
        voice="alloy",
        instructions="You are a concise voice assistant.",
        temperature=0.8,
    ),
)

await voice_agent.configure(llm=llm)
```

Install: `pip install "piopiy-ai[openai]"` · Env: `OPENAI_API_KEY`

---

## 3. Azure OpenAI Realtime

**Class:** `AzureRealtimeLLMService` (extends `OpenAIRealtimeLLMService`)

### Constructor parameters

```python
AzureRealtimeLLMService(
    *,
    api_key: str,        # Azure OpenAI API key
    base_url: str,       # full Azure WSS URL incl. api-version and deployment
    # plus all OpenAIRealtimeLLMService kwargs (session_properties etc.)
)
```

### Example

```python
from piopiy.services.azure.realtime.llm import AzureRealtimeLLMService
from piopiy.services.openai.realtime import events

llm = AzureRealtimeLLMService(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    base_url=(
        "wss://my-project.openai.azure.com/openai/realtime"
        "?api-version=2025-04-01-preview&deployment=my-realtime-deployment"
    ),
    session_properties=events.SessionProperties(voice="alloy"),
)

await voice_agent.configure(llm=llm)
```

Install: `pip install "piopiy-ai[azure]"` · Env: `AZURE_OPENAI_API_KEY`

---

## 4. AWS Nova Sonic

**Class:** `AWSNovaSonicLLMService`
**Modalities:** audio + text (input), audio + text (output)
**Function calling:** ✅ Yes

### Constructor parameters

```python
AWSNovaSonicLLMService(
    *,
    secret_access_key: str,
    access_key_id: str,
    region: str,                                # "us-east-1" | "us-west-2" | "ap-northeast-1"
    session_token: Optional[str] = None,
    model: str = "amazon.nova-2-sonic-v1:0",
    voice_id: str = "matthew",                  # see Nova voice docs
    params: Optional[Params] = None,
    system_instruction: Optional[str] = None,
    tools: Optional[ToolsSchema] = None,
)
```

`Params` (from `piopiy.services.aws.nova_sonic.llm`) wraps audio config and
inference settings (`temperature`, `top_p`, `max_tokens`, sample rate).

### Example

```python
from piopiy.services.aws.nova_sonic.llm import AWSNovaSonicLLMService

llm = AWSNovaSonicLLMService(
    secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    region="us-east-1",
    voice_id="matthew",
    system_instruction="You are a calm and helpful agent.",
)

await voice_agent.configure(llm=llm)
```

Install: `pip install "piopiy-ai[aws-nova-sonic]"` · Env: AWS credentials

---

## 5. Grok Realtime (xAI)

**Class:** `GrokRealtimeLLMService`
**Modalities:** audio (PCM, PCMU, PCMA at 8–48 kHz), text
**Function calling:** ✅ Yes (`web_search`, `x_search`, `file_search` built in, plus custom)
**Server-side VAD:** ✅ Yes

### Constructor parameters

```python
GrokRealtimeLLMService(
    *,
    api_key: str,                                            # xAI API key
    base_url: str = "wss://api.x.ai/v1/realtime",
    session_properties: Optional[SessionProperties] = None,  # voice ("Ara"|"Rex"|"Sal"|"Eve"|"Leo"), turn_detection, etc.
    start_audio_paused: bool = False,
)
```

### Example

```python
from piopiy.services.grok.realtime.llm import GrokRealtimeLLMService
from piopiy.services.grok.realtime import events

llm = GrokRealtimeLLMService(
    api_key=os.getenv("XAI_API_KEY"),
    session_properties=events.SessionProperties(voice="Rex"),
)

await voice_agent.configure(llm=llm)
```

Install: `pip install "piopiy-ai[grok]"` · Env: `XAI_API_KEY`

---

## 6. Ultravox (cloud realtime)

**Class:** `UltravoxRealtimeLLMService`
**Mode:** Audio-LLM hybrid — emits text, pair with a TTS

### Constructor parameters

```python
UltravoxRealtimeLLMService(
    *,
    api_key: str,
    params: Union[AgentInputParams, OneShotInputParams, JoinUrlInputParams],
    one_shot_selected_tools: Optional[ToolsSchema] = None,
)
```

### Example

```python
from piopiy.services.ultravox.llm import (
    UltravoxRealtimeLLMService, AgentInputParams,
)
from piopiy.services.cartesia.tts import CartesiaTTSService

llm = UltravoxRealtimeLLMService(
    api_key=os.getenv("ULTRAVOX_API_KEY"),
    params=AgentInputParams(agent_id=os.getenv("ULTRAVOX_AGENT_ID")),
)
tts = CartesiaTTSService(api_key=os.getenv("CARTESIA_API_KEY"))

# Audio-LLM hybrid: no `stt=`, but `tts=` is supplied
await voice_agent.configure(llm=llm, tts=tts)
```

Install: `pip install "piopiy-ai[ultravox,cartesia]"`

---

## 7. Ultravox (open-source / self-hosted)

**Class:** `UltravoxService`
**Mode:** Audio-LLM hybrid — runs against your own Ultravox WebSocket server
**Reference example:** [example/ultravox/ultravox.py](../example/ultravox/ultravox.py),
[example/opensource/hybrid.py](../example/opensource/hybrid.py)

### Constructor parameters

```python
UltravoxService(
    *,
    server_url: str = "ws://localhost:8766",
    language: Language = Language.EN,
    temperature: float = 0.2,
    max_tokens: int = 200,
    system_prompt: Optional[str] = None,
    persistent_connection: bool = True,
    ping_interval: float = 20.0,
    ping_timeout: float = 20.0,
)
```

### Example

```python
from piopiy.services.opensource.ultravox.omni import UltravoxService
from piopiy.transcriptions.language import Language
from piopiy.services.deepgram.tts import DeepgramTTSService

llm = UltravoxService(
    server_url="ws://localhost:8766",
    language=Language.EN,
    temperature=0.7,
    system_prompt="You are an advanced voice AI sales assistant.",
)
tts = DeepgramTTSService(api_key=os.getenv("DEEPGRAM_API_KEY"))

await voice_agent.configure(llm=llm, tts=tts)
```

Install: `pip install piopiy-ai`

---

## Choosing between models

| You want… | Pick |
|---|---|
| Lowest latency, audio-native model | **Gemini Live** or **OpenAI Realtime** |
| OpenAI ecosystem on Azure | **AzureRealtime** |
| AWS-native deployment | **AWS Nova Sonic** |
| xAI ecosystem with built-in search tools | **Grok Realtime** |
| Premium TTS voice, audio-LLM understanding | **Ultravox** + ElevenLabs / Cartesia |
| Fully self-hosted, no API keys | **UltravoxService** (open-source) + open-source TTS |

## See also

- [example/gemini_live/](../example/gemini_live/) — full Gemini Live agent
- [example/openai_realtime/](../example/openai_realtime/) — full OpenAI Realtime agent
- [example/aws_nova_sonic/](../example/aws_nova_sonic/) — full Nova Sonic agent
- [example/grok_realtime/](../example/grok_realtime/) — full Grok Realtime agent
- [example/azure_realtime/](../example/azure_realtime/) — full Azure Realtime agent
- [example/opensource/hybrid.py](../example/opensource/hybrid.py) — fully open-source hybrid
- [docs/CUSTOM_SERVICES.md](CUSTOM_SERVICES.md) — write your own realtime model
