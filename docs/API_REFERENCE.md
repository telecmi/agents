# API Reference

Complete API documentation for Piopiy AI SDK.

## Agent Class

The `Agent` class manages connections to Piopiy's signaling server and handles incoming calls.

### Constructor

```python
from piopiy.agent import Agent

agent = Agent(
    agent_id: str,
    agent_token: str,
    create_session: Callable,
    signaling_url: Optional[str] = None,
    debug: bool = False
)
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | `str` | Yes | - | Your Piopiy agent ID from the dashboard |
| `agent_token` | `str` | Yes | - | Your Piopiy agent token from the dashboard |
| `create_session` | `Callable` | Yes | - | Async function called for each incoming call |
| `signaling_url` | `str` | No | `https://signaling.piopiy.com` | Piopiy signaling server URL |
| `debug` | `bool` | No | `False` | Enable debug logging (INFO level) |

**Example:**

```python
agent = Agent(
    agent_id="your_agent_id",
    agent_token="your_agent_token",
    create_session=create_session,
    debug=True  # Enable verbose logging
)
```

### Methods

#### `connect()`

Connects to the Piopiy signaling server and starts listening for incoming calls.

```python
await agent.connect()
```

**Returns:** `None`

**Raises:** Connection errors if unable to connect to signaling server

#### `shutdown()`

Gracefully shuts down the agent and disconnects from the signaling server.

```python
await agent.shutdown()
```

**Returns:** `None`

### Context Variables

Access call context from anywhere in your code:

```python
from piopiy.agent import URL_CTX, TOKEN_CTX, ROOM_CTX

# Get current call context
url = URL_CTX.get()
token = TOKEN_CTX.get()
room = ROOM_CTX.get()
```

---

## VoiceAgent Class

The `VoiceAgent` class orchestrates the conversation flow between STT, LLM, and TTS services.

### Constructor

```python
from piopiy.voice_agent import VoiceAgent

voice_agent = VoiceAgent(
    instructions: str,
    greeting: str = "",
    initial_messages: Optional[List[dict]] = None,
    context_aggregator: Optional[Any] = None
)
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `instructions` | `str` | Yes | - | System prompt for the LLM |
| `greeting` | `str` | No | `""` | Initial message spoken to the caller |
| `initial_messages` | `List[dict]` | No | `None` | Pre-populate conversation history |
| `context_aggregator` | `Any` | No | `None` | Custom context management |

**Example:**

```python
voice_agent = VoiceAgent(
    instructions="You are a helpful customer service agent.",
    greeting="Hello! How can I help you today?",
    initial_messages=[
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello!"}
    ]
)
```

### Methods

#### `Action()`

Configures the voice agent with STT, LLM, and TTS services.

```python
await voice_agent.Action(
    stt: STTService,
    llm: LLMService,
    tts: TTSService,
    vad: bool = False,
    allow_interruptions: bool = False,
    interruption_strategy: Optional[InterruptionStrategy] = None
)
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `stt` | `STTService` | Yes | - | Speech-to-text service instance |
| `llm` | `LLMService` | Yes | - | Large language model service instance |
| `tts` | `TTSService` | Yes | - | Text-to-speech service instance |
| `vad` | `bool` | No | `False` | Enable voice activity detection |
| `allow_interruptions` | `bool` | No | `False` | Allow user to interrupt agent |
| `interruption_strategy` | `InterruptionStrategy` | No | `None` | Custom interruption logic |

**Returns:** `None`

**Example:**

```python
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy

await voice_agent.Action(
    stt=DeepgramSTTService(api_key="..."),
    llm=OpenAILLMService(api_key="..."),
    tts=CartesiaTTSService(api_key="..."),
    vad=True,
    allow_interruptions=True,
    interruption_strategy=MinWordsInterruptionStrategy(min_words=2)
)
```

#### `start()`

Starts the voice agent and begins the conversation loop.

```python
await voice_agent.start()
```

**Returns:** `None`

**Note:** This method blocks until the call ends.

---

## Service Interfaces

### STTService (Speech-to-Text)

Base interface for all STT providers.

**Common Providers:**

```python
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.whisper.stt import WhisperSTTService
from piopiy.services.assemblyai.stt import AssemblyAISTTService
from piopiy.services.google.stt import GoogleSTTService
from piopiy.services.azure.stt import AzureSTTService

# Example: Deepgram
stt = DeepgramSTTService(
    api_key: str,
    model: str = "nova-2",
    language: str = "en-US",
    interim_results: bool = True
)
```

**Common Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `api_key` | `str` | Provider API key |
| `model` | `str` | Model name/version |
| `language` | `str` | Language code (e.g., "en-US") |

### LLMService (Large Language Model)

Base interface for all LLM providers.

**Common Providers:**

```python
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.anthropic.llm import AnthropicLLMService
from piopiy.services.ollama.llm import OLLamaLLMService
from piopiy.services.groq.llm import GroqLLMService
from piopiy.services.google.llm import GoogleLLMService

# Example: OpenAI
llm = OpenAILLMService(
    api_key: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: int = 1000,
    tools: Optional[List[dict]] = None
)
```

**Common Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `api_key` | `str` | Provider API key |
| `model` | `str` | Model name |
| `temperature` | `float` | Randomness (0.0-2.0) |
| `max_tokens` | `int` | Maximum response length |
| `tools` | `List[dict]` | Function calling tools |

### TTSService (Text-to-Speech)

Base interface for all TTS providers.

**Common Providers:**

```python
from piopiy.services.cartesia.tts import CartesiaTTSService
from piopiy.services.elevenlabs.tts import ElevenLabsTTSService
from piopiy.services.playht.tts import PlayHTTTSService
from piopiy.services.google.tts import GoogleTTSService
from piopiy.services.azure.tts import AzureTTSService

# Example: Cartesia
tts = CartesiaTTSService(
    api_key: str,
    voice_id: str = "default",
    language: str = "en",
    speed: float = 1.0
)
```

**Common Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `api_key` | `str` | Provider API key |
| `voice_id` | `str` | Voice identifier |
| `language` | `str` | Language code |
| `speed` | `float` | Speech rate multiplier |

---

## Interruption Strategies

### MinWordsInterruptionStrategy

Interrupt after a minimum number of words are detected.

```python
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy

strategy = MinWordsInterruptionStrategy(min_words: int = 1)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_words` | `int` | `1` | Minimum words before interruption |

**Example:**

```python
# Interrupt immediately after first word
strategy = MinWordsInterruptionStrategy(min_words=1)

# Wait for 3 words before interrupting
strategy = MinWordsInterruptionStrategy(min_words=3)
```

### MinDurationInterruptionStrategy

Interrupt after a minimum duration of speech.

```python
from piopiy.audio.interruptions.min_duration_interruption_strategy import MinDurationInterruptionStrategy

strategy = MinDurationInterruptionStrategy(min_duration: float = 0.5)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_duration` | `float` | `0.5` | Minimum seconds before interruption |

---

## ServiceSwitcher

Dynamically switch between multiple service instances.

```python
from piopiy.services.service_switcher import ServiceSwitcher

switcher = ServiceSwitcher(
    services: Dict[str, Service],
    default: str
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `services` | `Dict[str, Service]` | Named service instances |
| `default` | `str` | Default service key |

**Methods:**

```python
# Switch to a different service
await switcher.switch_to(service_name: str)

# Get current service
current = switcher.current_service
```

**Example:**

```python
# Create multiple TTS voices
english_tts = CartesiaTTSService(voice_id="english_voice")
spanish_tts = CartesiaTTSService(voice_id="spanish_voice")

# Create switcher
tts_switcher = ServiceSwitcher(
    services={
        "english": english_tts,
        "spanish": spanish_tts
    },
    default="english"
)

# Use in agent
await voice_agent.Action(stt=stt, llm=llm, tts=tts_switcher)

# Switch during call
await tts_switcher.switch_to("spanish")
```

---

## Error Handling

### Common Exceptions

```python
# Connection errors
try:
    await agent.connect()
except ConnectionError as e:
    print(f"Failed to connect: {e}")

# Service errors
try:
    await voice_agent.start()
except Exception as e:
    print(f"Agent error: {e}")
```

---

## Type Hints

```python
from typing import Callable, Optional, List, Dict, Any

# create_session signature
async def create_session(
    agent_id: str,
    call_id: str,
    from_number: str,
    to_number: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    pass
```

---

## Next Steps

- **[Developer Guide](DEVELOPER_GUIDE.md)** - Learn how to use these APIs
- **[Examples](../example/README.md)** - See complete code examples
- **[Providers](PROVIDERS.md)** - Explore all supported providers
