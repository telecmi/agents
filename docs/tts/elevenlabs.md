# ElevenLabs TTS

```bash
pip install "piopiy-ai[elevenlabs]"
export ELEVENLABS_API_KEY=your_key
```

### Parameters

- `api_key`: API key for authentication
- `voice_id`: Voice identifier to use
- `model`: Model name to use (default `"eleven_turbo_v2_5"`)
- `url`: Endpoint URL (default `"wss://api.elevenlabs.io"`)
- `sample_rate`: Target audio sample rate
- `params`: Provider specific options
- `aggregate_sentences`: Aggregate sentences before synthesis (default `True`)


### Input Parameters

- `language`: Language for synthesis
- `stability`: Voice stability control
- `similarity_boost`: Similarity boost level
- `style`: Voice style control
- `use_speaker_boost`: Enable speaker boost
- `speed`: Voice speed control
- `auto_mode`: Enable automatic mode optimization
- `enable_ssml_parsing`: Enable SSML parsing
- `enable_logging`: Enable provider logging
- `apply_text_normalization`: Text normalization mode


### Example

```python
import os
from piopiy.services.elevenlabs.tts import ElevenLabsTTSService

tts = ElevenLabsTTSService(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
    voice_id="VOICE_ID",
    model="eleven_turbo_v2_5",
    sample_rate=24000,
)
```
