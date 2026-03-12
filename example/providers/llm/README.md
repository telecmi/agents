# Large Language Model (LLM) Provider Examples

This directory contains examples for different LLM providers supported by Piopiy AI.

## Available Providers

| Provider | Speed | Quality | Cost | Best For |
|----------|-------|---------|------|----------|
| **Groq** | ⚡⚡⚡ | ⭐⭐ | $ | Ultra-fast responses |
| **Cerebras** | ⚡⚡⚡ | ⭐⭐ | $ | Ultra-fast inference |
| **OpenAI** | ⚡⚡ | ⭐⭐⭐ | $$$ | Best overall quality |
| **Anthropic** | ⚡⚡ | ⭐⭐⭐ | $$$ | Complex reasoning |
| **Google Gemini** | ⚡⚡ | ⭐⭐⭐ | $$ | Multimodal |
| **Mistral** | ⚡⚡ | ⭐⭐⭐ | $$ | European AI |
| **DeepSeek** | ⚡⚡ | ⭐⭐ | $ | Cost-effective |
| **Perplexity** | ⚡⚡ | ⭐⭐⭐ | $$ | Search-augmented |
| **Together AI** | ⚡⚡ | ⭐⭐ | $ | Open-source models |
| **Fireworks** | ⚡⚡⚡ | ⭐⭐ | $ | Fast inference |
| **OpenRouter** | ⚡⚡ | ⭐⭐⭐ | $$ | Multi-provider access |
| **Ollama** | ⚡ | ⭐⭐ | Free | Local/offline |

## Examples

### anthropic.py
High-quality reasoning with Claude 3.5 Sonnet.

**Features**:
- Excellent reasoning
- Long context window
- Thoughtful responses
- Function calling

**Install**: `pip install "piopiy-ai[anthropic]" python-dotenv`  
**API Key**: https://console.anthropic.com/

### groq.py
Ultra-fast inference with Llama 3.3 70B.

**Features**:
- Fastest inference
- Low latency
- Good quality
- Cost-effective

**Install**: `pip install "piopiy-ai[groq]" python-dotenv`  
**API Key**: https://console.groq.com/

## Running Examples

```bash
python example/providers/llm/anthropic.py
python example/providers/llm/groq.py
```

## Environment Variables

```bash
# Required
AGENT_ID=your_agent_id
AGENT_TOKEN=your_agent_token

# LLM Providers
ANTHROPIC_API_KEY=your_key
GROQ_API_KEY=your_key

# STT & TTS (for examples)
DEEPGRAM_API_KEY=your_key
CARTESIA_API_KEY=your_key
```

## Choosing an LLM Provider

### For Speed
**Groq** - Best for applications where response time is critical.

### For Quality
**Anthropic Claude** - Best for complex reasoning and thoughtful responses.

## Configuration Examples

### Anthropic Claude
```python
llm = AnthropicLLMService(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    model="claude-3-5-sonnet-20241022",  # Latest Claude
    max_tokens=1024,
    temperature=0.7
)
```

### Groq
```python
llm = GroqLLMService(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",  # Fast and capable
    temperature=0.7
)
```

## Resources

- [Main Providers README](../README.md)
- [Developer Guide](../../../../docs/DEVELOPER_GUIDE.md)
- [Provider Documentation](../../../../docs/PROVIDERS.md)
