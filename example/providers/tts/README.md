# Text-to-Speech (TTS) Provider Examples

This directory contains examples for different TTS providers supported by Piopiy AI.

## Available Providers

| Provider | Speed | Quality | Cost | Best For |
|----------|-------|---------|------|----------|
| **Cartesia** | ⚡⚡⚡ | ⭐⭐⭐ | $$ | Ultra-low latency |
| **ElevenLabs** | ⚡⚡ | ⭐⭐⭐ | $$$ | Highest quality |
| **PlayHT** | ⚡⚡ | ⭐⭐⭐ | $$ | Voice cloning |
| **LMNT** | ⚡⚡⚡ | ⭐⭐⭐ | $$ | Low latency |
| **Deepgram Aura** | ⚡⚡⚡ | ⭐⭐ | $ | Fast, budget-friendly |
| **Azure** | ⚡⚡ | ⭐⭐ | $ | Enterprise, budget |
| **Google** | ⚡⚡ | ⭐⭐ | $ | Multi-language |
| **OpenAI** | ⚡⚡ | ⭐⭐⭐ | $$ | Good quality |
| **Rime** | ⚡⚡ | ⭐⭐ | $$ | General purpose |
| **Neuphonic** | ⚡⚡ | ⭐⭐ | $$ | Natural voices |
| **Fish Audio** | ⚡⚡ | ⭐⭐ | $$ | Voice synthesis |
| **Gradium** | ⚡⚡ | ⭐⭐ | $$ | General purpose |
| **Hume AI** | ⚡⚡ | ⭐⭐⭐ | $$$ | Empathic voice |
| **Speechmatics** | ⚡⚡ | ⭐⭐ | $$$ | Enterprise |
| **Groq** | ⚡⚡⚡ | ⭐⭐ | $ | Fast synthesis |
| **Murf.ai** | ⚡⚡ | ⭐⭐⭐ | $$$ | Professional voices |

## Examples

### cartesia.py
Ultra-low latency TTS with Cartesia Sonic.

**Features**:
- Fastest response time
- Natural-sounding voices
- Multiple languages

**Install**: `pip install "piopiy-ai[cartesia]" python-dotenv`  
**API Key**: https://play.cartesia.ai/

### elevenlabs.py
Highest quality, most expressive voices.

**Features**:
- Premium voice quality
- Emotional expression
- Voice cloning

**Install**: `pip install "piopiy-ai[elevenlabs]" python-dotenv`  
**API Key**: https://elevenlabs.io/

### playht.py
High-quality TTS with voice cloning.

**Features**:
- Voice cloning
- Multiple voices
- Good quality

**Install**: `pip install "piopiy-ai[playht]" python-dotenv`  
**API Key**: https://play.ht/

## Running Examples

```bash
# Run a specific TTS example
python example/providers/tts/cartesia.py
python example/providers/tts/elevenlabs.py
python example/providers/tts/playht.py
```

## Environment Variables

```bash
# Required
AGENT_ID=your_agent_id
AGENT_TOKEN=your_agent_token

# STT & LLM (for examples)
DEEPGRAM_API_KEY=your_key
OPENAI_API_KEY=your_key

# TTS Providers
CARTESIA_API_KEY=your_key
ELEVENLABS_API_KEY=your_key
PLAYHT_API_KEY=your_key
PLAYHT_USER_ID=your_user_id
MURF_API_KEY=your_key
```

## Choosing a TTS Provider

### For Low Latency
**Cartesia** - Best for real-time conversations where speed matters most.

### For Highest Quality
**ElevenLabs** - Best for premium applications where voice quality is critical.

### For Voice Cloning
**PlayHT** - Best when you need custom voice cloning capabilities.

### For Professional Voices
**Murf.ai** - Best for business/professional applications with extensive customization.

## Voice Configuration

### Cartesia
```python
tts = CartesiaTTSService(
    api_key=os.getenv("CARTESIA_API_KEY"),
    voice_id="a0e99841-438c-4a64-b679-ae501e7d6091",
    model="sonic-english",
    sample_rate=24000
)
```

### ElevenLabs
```python
tts = ElevenLabsTTSService(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
    voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel
    model="eleven_turbo_v2_5",
    stability=0.5,
    similarity_boost=0.75
)
```

### PlayHT
```python
tts = PlayHTTTSService(
    api_key=os.getenv("PLAYHT_API_KEY"),
    user_id=os.getenv("PLAYHT_USER_ID"),
    voice_id="s3://voice-cloning-zero-shot/...",
    sample_rate=24000
)
```

## Resources

- [Main Providers README](../README.md)
- [Developer Guide](../../../../docs/DEVELOPER_GUIDE.md)
- [Provider Documentation](../../../../docs/PROVIDERS.md)
