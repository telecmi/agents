# Speech-to-Text (STT) Provider Examples

This directory contains examples for different STT providers supported by Piopiy AI.

## Available Providers

| Provider | Speed | Accuracy | Cost | Best For |
|----------|-------|----------|------|----------|
| **Deepgram** | ⚡⚡⚡ | ⭐⭐⭐ | $$ | Real-time conversations |
| **AssemblyAI** | ⚡⚡ | ⭐⭐⭐ | $$ | High accuracy needed |
| **Azure** | ⚡⚡ | ⭐⭐⭐ | $$$ | Enterprise |
| **Google** | ⚡⚡ | ⭐⭐⭐ | $$ | Multi-language |
| **Gladia** | ⚡⚡ | ⭐⭐ | $$ | Real-time |
| **Speechmatics** | ⚡⚡ | ⭐⭐⭐ | $$$ | High accuracy |
| **OpenAI Whisper** | ⚡ | ⭐⭐⭐ | $$ | Cloud Whisper |
| **Local Whisper** | ⚡ | ⭐⭐⭐ | Free | Offline/privacy |

## Examples

### deepgram.py
Fast, accurate speech-to-text using Deepgram Nova-2.

**Features**:
- Ultra-low latency
- High accuracy
- Smart formatting
- Interim results

**Install**: `pip install "piopiy-ai[deepgram]" python-dotenv`  
**API Key**: https://console.deepgram.com/

### assemblyai.py
High-accuracy real-time transcription.

**Features**:
- Excellent accuracy
- Real-time streaming
- Word boosting
- Multiple languages

**Install**: `pip install "piopiy-ai[assemblyai]" python-dotenv`  
**API Key**: https://www.assemblyai.com/

## Running Examples

```bash
python example/providers/stt/deepgram.py
python example/providers/stt/assemblyai.py
```

## Environment Variables

```bash
# Required
AGENT_ID=your_agent_id
AGENT_TOKEN=your_agent_token

# STT Providers
DEEPGRAM_API_KEY=your_key
ASSEMBLYAI_API_KEY=your_key

# LLM & TTS (for examples)
OPENAI_API_KEY=your_key
CARTESIA_API_KEY=your_key
```

## Choosing an STT Provider

### For Speed
**Deepgram** - Best for real-time conversations where latency matters.

### For Accuracy
**AssemblyAI** - Best when transcription accuracy is critical.

## Configuration Examples

### Deepgram
```python
stt = DeepgramSTTService(
    api_key=os.getenv("DEEPGRAM_API_KEY"),
    model="nova-2",           # Latest model
    language="en-US",
    smart_format=True,        # Auto-formatting
    punctuate=True,           # Add punctuation
    interim_results=True      # Streaming results
)
```

### AssemblyAI
```python
stt = AssemblyAISTTService(
    api_key=os.getenv("ASSEMBLYAI_API_KEY"),
    sample_rate=16000,
    word_boost=["custom", "words"],  # Boost specific words
    encoding="pcm_s16le"
)
```

## Resources

- [Main Providers README](../README.md)
- [Developer Guide](../../../../docs/DEVELOPER_GUIDE.md)
- [Provider Documentation](../../../../docs/PROVIDERS.md)
