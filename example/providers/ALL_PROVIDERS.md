# All Provider Examples - Complete Reference

This document shows how to use every supported provider with Piopiy AI.

## Quick Reference Template

Every example follows this pattern:

```python
import asyncio
import os
from dotenv import load_dotenv
from piopiy.agent import Agent
from piopiy.voice_agent import VoiceAgent

# Import your chosen providers
from piopiy.services.{provider}.stt import {Provider}STTService
from piopiy.services.{provider}.llm import {Provider}LLMService
from piopiy.services.{provider}.tts import {Provider}TTSService

load_dotenv()

async def create_session(agent_id, call_id, from_number, to_number, metadata=None):
    voice_agent = VoiceAgent(
        instructions="You are a helpful AI assistant.",
        greeting="Hello! How can I help you?",
    )
    
    stt = {Provider}STTService(api_key=os.getenv("{PROVIDER}_API_KEY"))
    llm = {Provider}LLMService(api_key=os.getenv("{PROVIDER}_API_KEY"))
    tts = {Provider}TTSService(api_key=os.getenv("{PROVIDER}_API_KEY"))
    
    await voice_agent.Action(stt=stt, llm=llm, tts=tts, vad=True)
    await voice_agent.start()

async def main():
    agent = Agent(
        agent_id=os.getenv("AGENT_ID"),
        agent_token=os.getenv("AGENT_TOKEN"),
        create_session=create_session
    )
    await agent.connect()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Speech-to-Text (STT) Providers

### 1. Deepgram (Recommended for Speed)

```python
from piopiy.services.deepgram.stt import DeepgramSTTService

stt = DeepgramSTTService(
    api_key=os.getenv("DEEPGRAM_API_KEY"),
    model="nova-2",           # Options: nova-2, nova, base, enhanced
    language="en-US",         # Language code
    smart_format=True,        # Auto-formatting
    punctuate=True,           # Add punctuation
    interim_results=True      # Streaming results
)
```

**Install**: `pip install "piopiy-ai[deepgram]"`  
**API Key**: https://console.deepgram.com/

### 2. AssemblyAI

```python
from piopiy.services.assemblyai.stt import AssemblyAISTTService

stt = AssemblyAISTTService(
    api_key=os.getenv("ASSEMBLYAI_API_KEY"),
    sample_rate=16000,
    word_boost=["custom", "words"],  # Boost specific words
    encoding="pcm_s16le"
)
```

**Install**: `pip install "piopiy-ai[assemblyai]"`  
**API Key**: https://www.assemblyai.com/

### 3. Azure Speech

```python
from piopiy.services.azure.stt import AzureSTTService

stt = AzureSTTService(
    api_key=os.getenv("AZURE_SPEECH_KEY"),
    region=os.getenv("AZURE_SPEECH_REGION"),  # e.g., "eastus"
    language="en-US"
)
```

**Install**: `pip install "piopiy-ai[azure]"`  
**API Key**: https://portal.azure.com/

### 4. Google Cloud Speech

```python
from piopiy.services.google.stt import GoogleSTTService

stt = GoogleSTTService(
    credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
    language="en-US",
    model="latest_long"  # Options: latest_long, latest_short, command_and_search
)
```

**Install**: `pip install "piopiy-ai[google]"`  
**Setup**: https://cloud.google.com/speech-to-text

### 5. Whisper (Local/Cloud)

```python
from piopiy.services.whisper.stt import WhisperSTTService

stt = WhisperSTTService(
    model="base",  # Options: tiny, base, small, medium, large
    language="en"
)
```

**Install**: `pip install "piopiy-ai[whisper]"`  
**Note**: Runs locally, no API key needed

---

## Large Language Models (LLM)

### 1. OpenAI (Recommended for Quality)

```python
from piopiy.services.openai.llm import OpenAILLMService

llm = OpenAILLMService(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini",      # Options: gpt-4o, gpt-4o-mini, gpt-4-turbo
    temperature=0.7,          # 0-2, higher = more creative
    max_tokens=150,           # Max response length
    top_p=0.9                 # Nucleus sampling
)
```

**Install**: `pip install "piopiy-ai[openai]"`  
**API Key**: https://platform.openai.com/

### 2. Anthropic Claude

```python
from piopiy.services.anthropic.llm import AnthropicLLMService

llm = AnthropicLLMService(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    model="claude-3-5-sonnet-20241022",  # Latest Claude
    max_tokens=1024,
    temperature=0.7
)
```

**Install**: `pip install "piopiy-ai[anthropic]"`  
**API Key**: https://console.anthropic.com/

### 3. Groq (Fastest Inference)

```python
from piopiy.services.groq.llm import GroqLLMService

llm = GroqLLMService(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",  # Ultra-fast
    temperature=0.7
)
```

**Install**: `pip install "piopiy-ai[groq]"`  
**API Key**: https://console.groq.com/

### 4. Together AI

```python
from piopiy.services.together.llm import TogetherLLMService

llm = TogetherLLMService(
    api_key=os.getenv("TOGETHER_API_KEY"),
    model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    temperature=0.7
)
```

**Install**: `pip install "piopiy-ai[together]"`  
**API Key**: https://api.together.xyz/

### 5. Google Gemini

```python
from piopiy.services.google.llm import GoogleLLMService

llm = GoogleLLMService(
    api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-2.0-flash-exp",  # Latest Gemini
    temperature=0.7
)
```

**Install**: `pip install "piopiy-ai[google]"`  
**API Key**: https://makersuite.google.com/

---

## Text-to-Speech (TTS) Providers

### 1. Cartesia (Recommended for Latency)

```python
from piopiy.services.cartesia.tts import CartesiaTTSService

tts = CartesiaTTSService(
    api_key=os.getenv("CARTESIA_API_KEY"),
    voice_id="a0e99841-438c-4a64-b679-ae501e7d6091",  # British Lady
    model="sonic-english",    # Ultra-low latency
    sample_rate=24000
)
```

**Install**: `pip install "piopiy-ai[cartesia]"`  
**API Key**: https://play.cartesia.ai/

### 2. ElevenLabs (Highest Quality)

```python
from piopiy.services.elevenlabs.tts import ElevenLabsTTSService

tts = ElevenLabsTTSService(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
    voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel
    model="eleven_turbo_v2_5",
    stability=0.5,
    similarity_boost=0.75
)
```

**Install**: `pip install "piopiy-ai[elevenlabs]"`  
**API Key**: https://elevenlabs.io/

### 3. PlayHT

```python
from piopiy.services.playht.tts import PlayHTTTSService

tts = PlayHTTTSService(
    api_key=os.getenv("PLAYHT_API_KEY"),
    user_id=os.getenv("PLAYHT_USER_ID"),
    voice_id="s3://voice-cloning-zero-shot/...",
    sample_rate=24000
)
```

**Install**: `pip install "piopiy-ai[playht]"`  
**API Key**: https://play.ht/

### 4. Azure Neural TTS

```python
from piopiy.services.azure.tts import AzureTTSService

tts = AzureTTSService(
    api_key=os.getenv("AZURE_SPEECH_KEY"),
    region=os.getenv("AZURE_SPEECH_REGION"),
    voice="en-US-JennyNeural",  # Neural voice
    sample_rate=24000
)
```

**Install**: `pip install "piopiy-ai[azure]"`  
**API Key**: https://portal.azure.com/

### 5. Google Cloud TTS

```python
from piopiy.services.google.tts import GoogleTTSService

tts = GoogleTTSService(
    credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
    voice_id="en-US-Neural2-C",
    language="en-US",
    sample_rate=24000
)
```

**Install**: `pip install "piopiy-ai[google]"`  
**Setup**: https://cloud.google.com/text-to-speech

### 6. Murf.ai

```python
from pipecat_murf_tts import MurfTTSService

tts = MurfTTSService(
    api_key=os.getenv("MURF_API_KEY"),
    params=MurfTTSService.InputParams(
        voice_id="en-UK-ruby",
        style="Conversational",
        rate=0,
        pitch=0,
        sample_rate=44100,
        format="PCM"
    )
)
```

**Install**: `pip install pipecat-murf-tts`  
**API Key**: https://murf.ai/api/dashboard

---

## Recommended Combinations

### Ultra-Low Latency Stack
```python
stt = DeepgramSTTService(api_key=..., model="nova-2")
llm = GroqLLMService(api_key=..., model="llama-3.3-70b-versatile")
tts = CartesiaTTSService(api_key=..., model="sonic-english")
```

### Premium Quality Stack
```python
stt = AssemblyAISTTService(api_key=...)
llm = AnthropicLLMService(api_key=..., model="claude-3-5-sonnet-20241022")
tts = ElevenLabsTTSService(api_key=..., model="eleven_turbo_v2_5")
```

### Budget-Friendly Stack
```python
stt = DeepgramSTTService(api_key=..., model="base")
llm = OpenAILLMService(api_key=..., model="gpt-4o-mini")
tts = AzureTTSService(api_key=..., voice="en-US-JennyNeural")
```

### Multilingual Stack
```python
stt = GoogleSTTService(credentials_path=..., language="es-ES")
llm = GoogleLLMService(api_key=..., model="gemini-2.0-flash-exp")
tts = GoogleTTSService(credentials_path=..., voice_id="es-ES-Neural2-A")
```

---

## Environment Variables Template

```bash
# Piopiy (Required)
AGENT_ID=your_agent_id
AGENT_TOKEN=your_agent_token

# STT Providers
DEEPGRAM_API_KEY=your_key
ASSEMBLYAI_API_KEY=your_key
AZURE_SPEECH_KEY=your_key
AZURE_SPEECH_REGION=eastus
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# LLM Providers
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GROQ_API_KEY=your_key
TOGETHER_API_KEY=your_key
GOOGLE_API_KEY=your_key

# TTS Providers
CARTESIA_API_KEY=your_key
ELEVENLABS_API_KEY=your_key
PLAYHT_API_KEY=your_key
PLAYHT_USER_ID=your_user_id
MURF_API_KEY=your_key

# Optional
AGENT_DEBUG=false
```

## Next Steps

1. Choose your provider stack
2. Get API keys from provider websites
3. Install required packages
4. Copy the template code
5. Customize for your use case

## Resources

- [Provider Documentation](../../../docs/PROVIDERS.md)
- [Developer Guide](../../../docs/DEVELOPER_GUIDE.md)
- [Basic Example](../basic/)
