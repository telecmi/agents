# Combined Provider Stack Examples

This directory contains examples showing optimized combinations of STT, LLM, and TTS providers.

## Available Stacks

### fast_response.py - Ultra-Low Latency ⚡
Optimized for fastest possible response time.

**Stack**:
- STT: Deepgram Nova-2
- LLM: Groq Llama 3.3 70B
- TTS: Cartesia Sonic

**Best For**: Real-time conversations, customer service, interactive applications

**Install**: `pip install "piopiy-ai[deepgram,groq,cartesia,silero]"`

### high_quality.py - Premium Quality ⭐
Optimized for highest quality experience.

**Stack**:
- STT: AssemblyAI
- LLM: Claude 3.5 Sonnet
- TTS: ElevenLabs

**Best For**: Premium applications, professional services, high-value interactions

**Install**: `pip install "piopiy-ai[assemblyai,anthropic,elevenlabs,silero]"`

## Running Examples

```bash
# Ultra-low latency
python example/providers/combined/fast_response.py

# Premium quality
python example/providers/combined/high_quality.py
```

## Environment Variables

```bash
# Required
AGENT_ID=your_agent_id
AGENT_TOKEN=your_agent_token

# For fast_response.py
DEEPGRAM_API_KEY=your_key
GROQ_API_KEY=your_key
CARTESIA_API_KEY=your_key

# For high_quality.py
ASSEMBLYAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
ELEVENLABS_API_KEY=your_key
```

## Performance Comparison

| Stack | Latency | Quality | Cost/min | Use Case |
|-------|---------|---------|----------|----------|
| **Fast Response** | ~500ms | Good | $0.05 | Customer service, support |
| **High Quality** | ~1000ms | Excellent | $0.15 | Sales, consulting, premium |

## Customization

You can mix and match any providers:

```python
# Example: Fast STT + Quality LLM + Fast TTS
stt = DeepgramSTTService(...)      # Fast
llm = AnthropicLLMService(...)     # Quality
tts = CartesiaTTSService(...)      # Fast
```

## Resources

- [All Providers Reference](../ALL_PROVIDERS.md)
- [Main Providers README](../README.md)
- [Developer Guide](../../../../docs/DEVELOPER_GUIDE.md)
