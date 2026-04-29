# Complete Parameter Reference

This document provides a comprehensive reference of ALL parameters available in Piopiy AI SDK.

## Table of Contents

- [create_session Function](#create_session-function)
- [VoiceAgent Configuration](#voiceagent-configuration)
- [Speech-to-Text (STT) Services](#speech-to-text-stt-services)
- [Large Language Model (LLM) Services](#large-language-model-llm-services)
- [Text-to-Speech (TTS) Services](#text-to-speech-tts-services)
- [Agent Configuration](#agent-configuration)

---

## create_session Function

This function is called for **every incoming call** to your agent.

### Function Signature

```python
async def create_session(
    agent_id: str,
    call_id: str,
    from_number: str,
    to_number: str,
    metadata: dict = None
) -> None:
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | str | ✅ | Your agent's unique ID from the Piopiy dashboard |
| `call_id` | str | ✅ | Unique identifier for this call session |
| `from_number` | str | ✅ | Caller's phone number in E.164 format (e.g., "+14155551234") |
| `to_number` | str | ✅ | Called phone number in E.164 format (e.g., "+14155556789") |
| `metadata` | dict | ❌ | Optional custom data passed with the call |

### Metadata Usage

The `metadata` parameter allows you to pass custom data when initiating calls:

```python
# Example metadata structure
metadata = {
    "customer_id": "12345",
    "customer_name": "John Doe",
    "language": "en",
    "priority": "high",
    "department": "sales",
    "custom_field": "any value"
}

# Access in create_session
customer_name = metadata.get("customer_name", "Customer") if metadata else "Customer"
language = metadata.get("language", "en") if metadata else "en"
```

---

## VoiceAgent Configuration

### Constructor Parameters

```python
voice_agent = VoiceAgent(
    instructions="...",
    greeting="...",
    initial_messages=[...],
    end_of_turn_mode="auto"
)
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `instructions` | str | ✅ | - | System instructions for the AI agent |
| `greeting` | str | ✅ | - | First message spoken when call connects |
| `initial_messages` | list | ❌ | `[]` | Pre-populate conversation history |
| `end_of_turn_mode` | str | ❌ | `"auto"` | Turn-taking mode: `"auto"` or `"manual"` |

### configure() Method Parameters

```python
await voice_agent.configure(
    llm=llm_service,
    stt=stt_service,        # required for cascaded; omit for speech-to-speech
    tts=tts_service,        # required for cascaded; omit for speech-to-speech
    vad=True,               # bool | dict | SileroVADAnalyzer | None
    allow_interruptions=True,
)
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `llm` | LLMService | ✅ | - | Cascaded LLM **or** a realtime / audio-LLM model |
| `stt` | STTService | Cascaded only | `None` | Speech-to-Text service. Omit for speech-to-speech / audio-LLM modes |
| `tts` | TTSService | Cascaded / hybrid only | `None` | Text-to-Speech service. Omit for pure speech-to-speech |
| `vad` | bool / dict / analyzer | ❌ | `None` | Voice activity detection. `True` enables Silero with defaults |
| `allow_interruptions` | bool | ❌ | `True` | Allow user to interrupt the agent |
| `interruption_strategy` | InterruptionStrategy | ❌ | `None` | Override the default `MinWordsInterruptionStrategy` |
| `mcp_tools` | Any | ❌ | `None` | MCP client/tools to expose to the LLM |

> **`Action()` is still accepted** as a deprecated alias of `configure()`. Old
> code keeps working unchanged.

### VAD Parameters

```python
vad_params = {
    "threshold": 0.5,              # Detection sensitivity (0-1)
    "prefix_padding_ms": 300,      # Audio before speech (ms)
    "silence_duration_ms": 500     # Silence to detect end (ms)
}
```

---

## Speech-to-Text (STT) Services

### Deepgram STT

```python
from piopiy.services.deepgram.stt import DeepgramSTTService

stt = DeepgramSTTService(
    api_key="...",
    model="nova-2",
    language="en-US",
    smart_format=True,
    punctuate=True,
    interim_results=True,
    keywords=["custom", "words"]
)
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | str | ✅ | - | Deepgram API key |
| `model` | str | ❌ | `"nova-2"` | Model: `nova-2`, `nova`, `base`, `enhanced` |
| `language` | str | ❌ | `"en-US"` | Language code (e.g., `en-US`, `es-ES`) |
| `smart_format` | bool | ❌ | `True` | Auto-format numbers, dates |
| `punctuate` | bool | ❌ | `True` | Add punctuation |
| `interim_results` | bool | ❌ | `True` | Stream partial results |
| `keywords` | list | ❌ | `[]` | Boost specific words |

### AssemblyAI STT

```python
from piopiy.services.assemblyai.stt import AssemblyAISTTService

stt = AssemblyAISTTService(
    api_key="...",
    sample_rate=16000,
    word_boost=["custom", "words"],
    encoding="pcm_s16le"
)
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | str | ✅ | - | AssemblyAI API key |
| `sample_rate` | int | ❌ | `16000` | Audio sample rate |
| `word_boost` | list | ❌ | `[]` | Boost specific words |
| `encoding` | str | ❌ | `"pcm_s16le"` | Audio encoding |

### Azure STT

```python
from piopiy.services.azure.stt import AzureSTTService

stt = AzureSTTService(
    api_key="...",
    region="eastus",
    language="en-US"
)
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | str | ✅ | - | Azure Speech key |
| `region` | str | ✅ | - | Azure region (e.g., `eastus`) |
| `language` | str | ❌ | `"en-US"` | Language code |

### Google Cloud STT

```python
from piopiy.services.google.stt import GoogleSTTService

stt = GoogleSTTService(
    credentials_path="/path/to/credentials.json",
    language="en-US",
    model="latest_long"
)
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `credentials_path` | str | ✅ | - | Path to Google credentials JSON |
| `language` | str | ❌ | `"en-US"` | Language code |
| `model` | str | ❌ | `"latest_long"` | Model: `latest_long`, `latest_short` |

---

## Large Language Model (LLM) Services

### OpenAI LLM

```python
from piopiy.services.openai.llm import OpenAILLMService

llm = OpenAILLMService(
    api_key="...",
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=150,
    top_p=0.9,
    tools=[...]
)
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | str | ✅ | - | OpenAI API key |
| `model` | str | ❌ | `"gpt-4o-mini"` | Model: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` |
| `temperature` | float | ❌ | `0.7` | Creativity (0-2, higher = more creative) |
| `max_tokens` | int | ❌ | `150` | Max response length |
| `top_p` | float | ❌ | `0.9` | Nucleus sampling (0-1) |
| `tools` | list | ❌ | `[]` | Function calling tools |

### Anthropic Claude LLM

```python
from piopiy.services.anthropic.llm import AnthropicLLMService

llm = AnthropicLLMService(
    api_key="...",
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    temperature=0.7
)
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | str | ✅ | - | Anthropic API key |
| `model` | str | ❌ | `"claude-3-5-sonnet-20241022"` | Claude model version |
| `max_tokens` | int | ❌ | `1024` | Max response length |
| `temperature` | float | ❌ | `0.7` | Creativity (0-1) |

### Groq LLM

```python
from piopiy.services.groq.llm import GroqLLMService

llm = GroqLLMService(
    api_key="...",
    model="llama-3.3-70b-versatile",
    temperature=0.7
)
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | str | ✅ | - | Groq API key |
| `model` | str | ❌ | `"llama-3.3-70b-versatile"` | Model name |
| `temperature` | float | ❌ | `0.7` | Creativity (0-2) |

---

## Text-to-Speech (TTS) Services

### Cartesia TTS

```python
from piopiy.services.cartesia.tts import CartesiaTTSService

tts = CartesiaTTSService(
    api_key="...",
    voice_id="a0e99841-438c-4a64-b679-ae501e7d6091",
    model="sonic-english",
    sample_rate=24000,
    speed=1.0
)
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | str | ✅ | - | Cartesia API key |
| `voice_id` | str | ✅ | - | Voice ID from Cartesia |
| `model` | str | ❌ | `"sonic-english"` | Model name |
| `sample_rate` | int | ❌ | `24000` | Audio sample rate (8000-44100) |
| `speed` | float | ❌ | `1.0` | Speech rate (0.5-2.0) |

### ElevenLabs TTS

```python
from piopiy.services.elevenlabs.tts import ElevenLabsTTSService

tts = ElevenLabsTTSService(
    api_key="...",
    voice_id="21m00Tcm4TlvDq8ikWAM",
    model="eleven_turbo_v2_5",
    stability=0.5,
    similarity_boost=0.75
)
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | str | ✅ | - | ElevenLabs API key |
| `voice_id` | str | ✅ | - | Voice ID from ElevenLabs |
| `model` | str | ❌ | `"eleven_turbo_v2_5"` | Model name |
| `stability` | float | ❌ | `0.5` | Voice stability (0-1) |
| `similarity_boost` | float | ❌ | `0.75` | Voice clarity (0-1) |

### OpenAI TTS

```python
from piopiy.services.openai.tts import OpenAITTSService

tts = OpenAITTSService(
    api_key="...",
    voice="alloy",
    model="tts-1",
    sample_rate=24000
)
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_key` | str | ✅ | - | OpenAI API key |
| `voice` | str | ❌ | `"alloy"` | Voice: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer` |
| `model` | str | ❌ | `"tts-1"` | Model: `tts-1`, `tts-1-hd` |
| `sample_rate` | int | ❌ | `24000` | Audio sample rate |

---

## Agent Configuration

```python
from piopiy.agent import Agent

agent = Agent(
    agent_id="...",
    agent_token="...",
    create_session=create_session,
    debug=False,
    on_call_started=lambda call_id: print(f"Started: {call_id}"),
    on_call_ended=lambda call_id: print(f"Ended: {call_id}")
)
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | str | ✅ | - | Your agent ID from dashboard |
| `agent_token` | str | ✅ | - | Your agent token from dashboard |
| `create_session` | callable | ✅ | - | Session creation callback function |
| `debug` | bool | ❌ | `False` | Enable verbose logging |
| `on_call_started` | callable | ❌ | `None` | Callback when call starts |
| `on_call_ended` | callable | ❌ | `None` | Callback when call ends |

---

## Complete Example

See [`example/basic/basic.py`](../example/basic/basic.py) for a complete example showing all parameters in use.

## Provider-Specific Documentation

For detailed provider-specific parameters, see:
- [STT Providers](../example/providers/stt/README.md)
- [LLM Providers](../example/providers/llm/README.md)
- [TTS Providers](../example/providers/tts/README.md)
