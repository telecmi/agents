# Murf.ai TTS Examples

This directory contains examples demonstrating how to use [Murf.ai](https://murf.ai) TTS with Piopiy AI.

## About Murf.ai

Murf.ai provides high-quality, natural-sounding AI voices with extensive customization options including:
- **40+ voices** across multiple languages and accents
- **Voice styles**: Conversational, Narration, and more
- **Fine-tuning**: Adjust rate, pitch, and variation
- **Custom pronunciations**: Define how specific words are spoken
- **Multiple audio formats**: PCM, WAV, MP3, FLAC, OGG, and more

## Installation

```bash
# Install Piopiy with required providers
pip install "piopiy-ai[deepgram,openai,silero]" python-dotenv

# Install Murf.ai TTS package
pip install pipecat-murf-tts
```

## Get Your API Key

1. Sign up at [Murf AI Dashboard](https://murf.ai/api/dashboard)
2. Get your API key from the dashboard
3. Add it to your `.env` file:

```bash
MURF_API_KEY=your_murf_api_key_here
```

## Examples

### murf_tts.py

Basic voice agent using Murf.ai TTS with Deepgram STT and OpenAI LLM.

**Features**:
- British English voice (en-UK-ruby)
- Conversational style
- Full configuration examples for all Murf.ai parameters

**Run**:
```bash
python example/murf/murf_tts.py
```

## Available Voices

Murf.ai offers a wide variety of voices. Some popular options:

**English (US)**:
- `en-US-natalie` - Female, professional
- `en-US-amara` - Female, warm
- `en-US-marcus` - Male, authoritative

**English (UK)**:
- `en-UK-ruby` - Female, conversational
- `en-UK-oliver` - Male, professional

**Other Languages**:
- Spanish, French, German, Italian, Portuguese, Hindi, and more

Visit the [Murf AI Voice Library](https://murf.ai/api/dashboard) to explore all available voices.

## Configuration Options

The Murf.ai TTS service supports extensive configuration:

```python
from pipecat_murf_tts import MurfTTSService

tts = MurfTTSService(
    api_key="your-api-key",
    params=MurfTTSService.InputParams(
        voice_id="en-UK-ruby",        # Voice selection
        style="Conversational",        # Voice style
        rate=0,                        # Speech rate (-50 to 50)
        pitch=0,                       # Pitch (-50 to 50)
        variation=1,                   # Variation (0-5, Gen2 only)
        model="FALCON",                # Model: FALCON or GEN2
        sample_rate=44100,             # Audio quality
        channel_type="MONO",           # MONO or STEREO
        format="PCM",                  # Audio format
        multi_native_locale="en-US",   # Language (Gen2)
        pronunciation_dictionary={     # Custom pronunciations
            "Piopiy": {"pronunciation": "pie-oh-pie"},
        },
    ),
)
```

## Environment Variables

Create a `.env` file with:

```bash
# Required
AGENT_ID=your_agent_id
AGENT_TOKEN=your_agent_token
MURF_API_KEY=your_murf_api_key

# For the example
DEEPGRAM_API_KEY=your_deepgram_key
OPENAI_API_KEY=your_openai_key

# Optional
AGENT_DEBUG=true  # Enable verbose logging
```

## Resources

- [Murf AI Website](https://murf.ai)
- [Murf AI API Dashboard](https://murf.ai/api/dashboard)
- [Pipecat Murf TTS GitHub](https://github.com/murf-ai/pipecat-murf-tts)
- [Murf AI Voice Library](https://murf.ai/api/dashboard)

## Support

For Murf.ai specific questions, visit their [support page](https://murf.ai/support).
For Piopiy integration issues, check the main [Piopiy documentation](../../README.md).
