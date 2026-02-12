# Developer Guide

This comprehensive guide covers everything you need to build production-ready voice AI agents with Piopiy AI.

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Building Voice Agents](#building-voice-agents)
3. [Advanced Features](#advanced-features)
4. [Best Practices](#best-practices)
5. [Performance Optimization](#performance-optimization)

---

## Core Concepts

### Agent Architecture

Piopiy AI uses a **session-based architecture** where each incoming call creates a new session:

```
Incoming Call → create_session() → VoiceAgent → Audio Pipeline → Conversation Loop
```

**Key Components:**

- **Agent**: Manages connections to Piopiy's signaling server and handles incoming calls
- **VoiceAgent**: Orchestrates the conversation flow (STT → LLM → TTS)
- **Services**: Pluggable providers for STT, LLM, and TTS
- **Transport**: Handles audio streaming (WebRTC, WebSocket, etc.)

### The create_session Callback

This is the heart of your voice agent. It's called for every incoming call:

```python
async def create_session(
    agent_id: str,
    call_id: str,
    from_number: str,
    to_number: str,
    metadata: dict = None
):
    # Your agent logic here
    pass
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_id` | `str` | Your Piopiy agent ID |
| `call_id` | `str` | Unique identifier for this call |
| `from_number` | `str` | Caller's phone number |
| `to_number` | `str` | Called phone number (your agent's number) |
| `metadata` | `dict` | Custom data passed with the call (optional) |

### Metadata Handling

Metadata allows you to pass custom data to your agent:

```python
async def create_session(call_id, metadata=None, **kwargs):
    if metadata:
        customer_id = metadata.get("customer_id")
        language = metadata.get("lang", "en")
        priority = metadata.get("priority", 1)
        
        # Route based on metadata
        if priority > 5:
            voice_agent = VoiceAgent(
                instructions="You are a priority support agent...",
                greeting=f"Hello valued customer! I see you're calling about {metadata.get('topic')}."
            )
```

**Automatic JSON Parsing**: Piopiy automatically parses JSON strings into Python dictionaries.

### Debug Mode

Control logging verbosity:

```python
agent = Agent(
    agent_id=os.getenv("AGENT_ID"),
    agent_token=os.getenv("AGENT_TOKEN"),
    create_session=create_session,
    debug=True  # Enable detailed logging
)
```

- **`debug=True`**: Full INFO-level logs, including provider internals
- **`debug=False`** (default): ERROR-level only, clean console output

---

## Building Voice Agents

### VoiceAgent Configuration

```python
from piopiy.voice_agent import VoiceAgent

voice_agent = VoiceAgent(
    instructions="You are a helpful customer service agent. Be professional and concise.",
    greeting="Thank you for calling. How may I assist you today?",
    # Optional parameters:
    # initial_messages=[...],  # Pre-populate conversation history
    # context_aggregator=...,  # Custom context management
)
```

**Instructions Best Practices:**

✅ **Good:**
```python
instructions = """
You are a restaurant reservation assistant.
- Ask for date, time, party size, and name
- Confirm availability before booking
- Be friendly but efficient
- If fully booked, offer alternative times
"""
```

❌ **Avoid:**
```python
instructions = "Help with reservations"  # Too vague
```

### Provider Selection

#### Speech-to-Text (STT)

```python
from piopiy.services.deepgram.stt import DeepgramSTTService
from piopiy.services.whisper.stt import WhisperSTTService

# Cloud option (low latency)
stt = DeepgramSTTService(
    api_key=os.getenv("DEEPGRAM_API_KEY"),
    model="nova-2",  # Latest model
    language="en-US"
)

# Open-source option
stt = WhisperSTTService(
    model="medium",  # small, medium, large
    language="en"
)
```

#### Large Language Model (LLM)

```python
from piopiy.services.openai.llm import OpenAILLMService
from piopiy.services.anthropic.llm import AnthropicLLMService
from piopiy.services.ollama.llm import OLLamaLLMService

# OpenAI
llm = OpenAILLMService(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini"  # Fast and cost-effective
)

# Anthropic Claude
llm = AnthropicLLMService(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    model="claude-3-5-sonnet-20241022"
)

# Local Ollama
llm = OLLamaLLMService(
    model="llama3.1",
    base_url="http://localhost:11434"
)
```

#### Text-to-Speech (TTS)

```python
from piopiy.services.cartesia.tts import CartesiaTTSService
from piopiy.services.elevenlabs.tts import ElevenLabsTTSService

# Cartesia (low latency)
tts = CartesiaTTSService(
    api_key=os.getenv("CARTESIA_API_KEY"),
    voice_id="bdab08ad-4137-4548-b9db-6142854c7525"  # Professional voice
)

# ElevenLabs (high quality)
tts = ElevenLabsTTSService(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
    voice_id="21m00Tcm4TlvDq8ikWAM"  # Rachel voice
)
```

### Voice Activity Detection (VAD)

Enable interruption handling with Silero VAD:

```bash
pip install "piopiy-ai[silero]"
```

```python
from piopiy.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy

await voice_agent.Action(
    stt=stt,
    llm=llm,
    tts=tts,
    vad=True,  # Enable VAD
    allow_interruptions=True,  # Allow user to interrupt
    interruption_strategy=MinWordsInterruptionStrategy(min_words=1)
)
```

**Interruption Strategies:**

- `MinWordsInterruptionStrategy(min_words=1)`: Interrupt after N words
- `MinDurationInterruptionStrategy(min_duration=0.5)`: Interrupt after N seconds
- Custom strategies: Implement your own logic

---

## Advanced Features

### Function Calling & Tools

Enable your agent to call external functions:

```python
from piopiy.services.openai.llm import OpenAILLMService

# Define tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g., San Francisco"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

llm = OpenAILLMService(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini",
    tools=tools
)

# Implement tool handlers
async def handle_function_call(function_name, arguments):
    if function_name == "get_weather":
        location = arguments.get("location")
        # Call your weather API
        return {"temperature": 72, "condition": "sunny"}
```

See [example/function_calling](../example/function_calling) for complete examples.

### Dynamic Provider Switching

Switch providers mid-call based on user input or context:

```python
from piopiy.services.service_switcher import ServiceSwitcher

# Create multiple TTS services
english_tts = CartesiaTTSService(voice_id="english_voice_id")
spanish_tts = CartesiaTTSService(voice_id="spanish_voice_id")

# Wrap in switcher
tts_switcher = ServiceSwitcher(
    services={
        "english": english_tts,
        "spanish": spanish_tts
    },
    default="english"
)

await voice_agent.Action(stt=stt, llm=llm, tts=tts_switcher)

# Switch during conversation
await tts_switcher.switch_to("spanish")
```

See [example/switch_providers](../example/switch_providers) for complete examples.

### Context Management

Maintain conversation context across turns:

```python
from piopiy.services.openai.context import OpenAIUserContextAggregator

# Pre-populate context
initial_messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "My name is John."},
    {"role": "assistant", "content": "Nice to meet you, John!"}
]

voice_agent = VoiceAgent(
    instructions="Remember user preferences from previous messages.",
    greeting="Welcome back!",
    initial_messages=initial_messages
)
```

### Error Handling

Handle errors gracefully:

```python
async def create_session(call_id, **kwargs):
    try:
        voice_agent = VoiceAgent(
            instructions="You are a helpful assistant.",
            greeting="Hello!"
        )
        
        stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
        llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
        tts = CartesiaTTSService(api_key=os.getenv("CARTESIA_API_KEY"))
        
        await voice_agent.Action(stt=stt, llm=llm, tts=tts)
        await voice_agent.start()
        
    except Exception as e:
        print(f"❌ Error in call {call_id}: {e}")
        # Log to monitoring service
        # Optionally play error message to caller
```

---

## Best Practices

### 1. Keep Instructions Clear and Specific

```python
# ✅ Good
instructions = """
You are a pizza ordering assistant.
1. Greet the customer
2. Ask for pizza size (small, medium, large)
3. Ask for toppings
4. Confirm order and total price
5. Get delivery address
Be friendly and confirm each step.
"""

# ❌ Avoid
instructions = "Take pizza orders"
```

### 2. Use Appropriate Models

| Use Case | Recommended LLM | Recommended TTS |
|----------|----------------|-----------------|
| Customer support | GPT-4o-mini, Claude 3.5 Sonnet | Cartesia, ElevenLabs |
| Quick Q&A | GPT-3.5-turbo, Llama 3.1 | Cartesia |
| Complex reasoning | GPT-4o, Claude 3.5 Sonnet | ElevenLabs |
| Multilingual | GPT-4o, Claude 3.5 Sonnet | Google, Azure |
| Privacy-focused | Ollama (local) | Piper, XTTS (local) |

### 3. Optimize Latency

```python
# Use streaming services
stt = DeepgramSTTService(model="nova-2")  # Fast streaming
llm = OpenAILLMService(model="gpt-4o-mini")  # Low latency
tts = CartesiaTTSService()  # Sub-second TTFB

# Enable VAD for natural interruptions
await voice_agent.Action(
    stt=stt, llm=llm, tts=tts,
    vad=True,
    allow_interruptions=True
)
```

### 4. Handle Metadata Effectively

```python
async def create_session(call_id, metadata=None, **kwargs):
    # Default values
    language = "en"
    customer_tier = "standard"
    
    if metadata:
        language = metadata.get("lang", "en")
        customer_tier = metadata.get("tier", "standard")
    
    # Customize based on metadata
    if customer_tier == "premium":
        greeting = "Thank you for being a valued premium member!"
    else:
        greeting = "Thank you for calling!"
    
    voice_agent = VoiceAgent(
        instructions=f"Respond in {language}. Customer tier: {customer_tier}",
        greeting=greeting
    )
```

### 5. Log Important Events

```python
async def create_session(call_id, from_number, to_number, metadata=None, **kwargs):
    print(f"📞 Call started: {call_id}")
    print(f"   From: {from_number}, To: {to_number}")
    
    if metadata:
        print(f"   Metadata: {metadata}")
    
    try:
        # Agent logic
        await voice_agent.start()
    except Exception as e:
        print(f"❌ Call {call_id} failed: {e}")
    finally:
        print(f"📴 Call ended: {call_id}")
```

---

## Performance Optimization

### Reduce Latency

1. **Choose Low-Latency Providers**:
   - STT: Deepgram Nova-2, AssemblyAI
   - LLM: GPT-4o-mini, Claude 3.5 Haiku
   - TTS: Cartesia, PlayHT

2. **Enable Streaming**: All services stream by default

3. **Optimize Instructions**: Shorter instructions = faster LLM responses

4. **Use VAD**: Reduces unnecessary processing

### Reduce Costs

1. **Use Cost-Effective Models**:
   ```python
   llm = OpenAILLMService(model="gpt-4o-mini")  # 15x cheaper than GPT-4
   ```

2. **Implement Caching**: Cache common responses

3. **Use Open-Source for Development**:
   ```python
   llm = OLLamaLLMService(model="llama3.1")  # Free local inference
   stt = WhisperSTTService(model="small")  # Free local transcription
   ```

### Monitor Performance

```python
import time

async def create_session(call_id, **kwargs):
    start_time = time.time()
    
    try:
        # Agent logic
        await voice_agent.start()
    finally:
        duration = time.time() - start_time
        print(f"⏱️  Call {call_id} duration: {duration:.2f}s")
```

---

## Next Steps

- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Examples](../example/README.md)** - More code examples
- **[Providers](PROVIDERS.md)** - Explore all supported providers
- **[Telephony Setup](TELEPHONY.md)** - Deploy to production

## Need Help?

- **GitHub Issues**: [Report bugs](https://github.com/telecmi/agents/issues)
- **Email**: support@piopiy.com
