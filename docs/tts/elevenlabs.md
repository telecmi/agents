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
