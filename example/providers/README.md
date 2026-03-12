# Provider Examples

This directory contains examples demonstrating how to use different AI providers with Piopiy.

## Directory Structure

```
providers/
├── stt/          # Speech-to-Text providers
├── llm/          # Large Language Model providers
├── tts/          # Text-to-Speech providers
└── combined/     # Mix-and-match provider combinations
```

## Available Providers

### Speech-to-Text (STT)

| Provider | Example | Features |
|----------|---------|----------|
| **Deepgram** | `stt/deepgram.py` | Fast, accurate, Nova-2 model |
| **AssemblyAI** | `stt/assemblyai.py` | Real-time transcription |
| **Azure** | `stt/azure.py` | Microsoft Speech Services |
| **Google** | `stt/google.py` | Google Cloud Speech-to-Text |
| **Whisper** | `stt/whisper.py` | OpenAI Whisper (local/cloud) |

### Large Language Models (LLM)

| Provider | Example | Features |
|----------|---------|----------|
| **OpenAI** | `llm/openai.py` | GPT-4o, GPT-4o-mini |
| **Anthropic** | `llm/anthropic.py` | Claude 3.5 Sonnet |
| **Groq** | `llm/groq.py` | Ultra-fast inference |
| **Together** | `llm/together.py` | Open-source models |
| **Google** | `llm/google.py` | Gemini models |

### Text-to-Speech (TTS)

| Provider | Example | Features |
|----------|---------|----------|
| **Cartesia** | `tts/cartesia.py` | Low-latency, natural voices |
| **ElevenLabs** | `tts/elevenlabs.py` | High-quality, expressive |
| **PlayHT** | `tts/playht.py` | Voice cloning |
| **Azure** | `tts/azure.py` | Microsoft Neural TTS |
| **Google** | `tts/google.py` | Google Cloud TTS |
| **Murf.ai** | `tts/murf.py` | Professional voices |

## Combined Examples

Mix and match providers for optimal performance:

| Example | STT | LLM | TTS | Use Case |
|---------|-----|-----|-----|----------|
| `combined/fast_response.py` | Deepgram | Groq | Cartesia | Ultra-low latency |
| `combined/high_quality.py` | AssemblyAI | Claude | ElevenLabs | Premium quality |
| `combined/cost_optimized.py` | Deepgram | GPT-4o-mini | Azure | Budget-friendly |
| `combined/multilingual.py` | Google | Gemini | Google | Multi-language support |

## Installation

Install providers you want to use:

```bash
# STT providers
pip install "piopiy-ai[deepgram]" python-dotenv      # Deepgram
pip install "piopiy-ai[assemblyai]" python-dotenv    # AssemblyAI
pip install "piopiy-ai[azure]" python-dotenv         # Azure
pip install "piopiy-ai[google]" python-dotenv        # Google
pip install "piopiy-ai[whisper]" python-dotenv       # Whisper

# LLM providers
pip install "piopiy-ai[openai]" python-dotenv        # OpenAI
pip install "piopiy-ai[anthropic]" python-dotenv     # Anthropic
pip install "piopiy-ai[groq]" python-dotenv          # Groq
pip install "piopiy-ai[together]" python-dotenv      # Together
pip install "piopiy-ai[google]" python-dotenv        # Google Gemini

# TTS providers
pip install "piopiy-ai[cartesia]" python-dotenv      # Cartesia
pip install "piopiy-ai[elevenlabs]" python-dotenv    # ElevenLabs
pip install "piopiy-ai[playht]" python-dotenv        # PlayHT
pip install "piopiy-ai[azure]" python-dotenv         # Azure
pip install "piopiy-ai[google]" python-dotenv        # Google
pip install pipecat-murf-tts           # Murf.ai

# Install multiple at once
pip install "piopiy-ai[deepgram,openai,cartesia,silero]" python-dotenv
```

## Environment Variables

Each provider requires API keys. Create a `.env` file:

```bash
# Piopiy (required)
AGENT_ID=your_agent_id
AGENT_TOKEN=your_agent_token

# STT Providers
DEEPGRAM_API_KEY=your_key
ASSEMBLYAI_API_KEY=your_key
AZURE_SPEECH_KEY=your_key
AZURE_SPEECH_REGION=your_region
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# LLM Providers
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GROQ_API_KEY=your_key
TOGETHER_API_KEY=your_key

# TTS Providers
CARTESIA_API_KEY=your_key
ELEVENLABS_API_KEY=your_key
PLAYHT_API_KEY=your_key
PLAYHT_USER_ID=your_user_id
MURF_API_KEY=your_key
```

## Running Examples

```bash
# Run a specific provider example
python example/providers/stt/deepgram.py
python example/providers/llm/anthropic.py
python example/providers/tts/elevenlabs.py

# Run a combined example
python example/providers/combined/fast_response.py
```

## Provider Comparison

### STT Providers

| Provider | Speed | Accuracy | Cost | Best For |
|----------|-------|----------|------|----------|
| Deepgram | ⚡⚡⚡ | ⭐⭐⭐ | $$ | Real-time conversations |
| AssemblyAI | ⚡⚡ | ⭐⭐⭐ | $$ | High accuracy needed |
| Azure | ⚡⚡ | ⭐⭐⭐ | $$$ | Enterprise |
| Google | ⚡⚡ | ⭐⭐⭐ | $$ | Multi-language |
| Whisper | ⚡ | ⭐⭐⭐ | Free (local) | Offline/budget |

### LLM Providers

| Provider | Speed | Quality | Cost | Best For |
|----------|-------|---------|------|----------|
| Groq | ⚡⚡⚡ | ⭐⭐ | $ | Ultra-fast responses |
| OpenAI | ⚡⚡ | ⭐⭐⭐ | $$$ | Best overall quality |
| Anthropic | ⚡⚡ | ⭐⭐⭐ | $$$ | Complex reasoning |
| Together | ⚡⚡ | ⭐⭐ | $ | Open-source models |
| Google | ⚡⚡ | ⭐⭐⭐ | $$ | Multimodal |

### TTS Providers

| Provider | Speed | Quality | Cost | Best For |
|----------|-------|---------|------|----------|
| Cartesia | ⚡⚡⚡ | ⭐⭐⭐ | $$ | Low latency |
| ElevenLabs | ⚡⚡ | ⭐⭐⭐ | $$$ | Highest quality |
| PlayHT | ⚡⚡ | ⭐⭐⭐ | $$ | Voice cloning |
| Murf.ai | ⚡⚡ | ⭐⭐⭐ | $$$ | Professional voices |
| Azure | ⚡⚡ | ⭐⭐ | $ | Budget-friendly |
| Google | ⚡⚡ | ⭐⭐ | $ | Multi-language |

## Choosing Providers

### For Low Latency
```
STT: Deepgram
LLM: Groq
TTS: Cartesia
```

### For Highest Quality
```
STT: AssemblyAI
LLM: Claude 3.5 Sonnet
TTS: ElevenLabs
```

### For Budget
```
STT: Deepgram
LLM: GPT-4o-mini
TTS: Azure
```

### For Multilingual
```
STT: Google
LLM: Gemini
TTS: Google
```

## Next Steps

1. Browse individual provider examples
2. Test different combinations
3. Compare performance and quality
4. Choose the best stack for your use case

## Resources

- [Main README](../../../README.md)
- [Developer Guide](../../../docs/DEVELOPER_GUIDE.md)
- [Provider Documentation](../../../docs/PROVIDERS.md)
