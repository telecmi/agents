# Deepgram TTS

```bash
pip install "piopiy-ai[deepgram]"
export DEEPGRAM_API_KEY=your_key
```

### Parameters

- `api_key`: API key for authentication
- `voice`: Voice identifier to use (default `"aura-2-helena-en"`)
- `base_url`: Override API base URL (default `""`)
- `sample_rate`: Target audio sample rate
- `encoding`: Audio encoding (default `"linear16"`)


### Input Parameters

None


### Example

```python
import os
from piopiy.services.deepgram.tts import DeepgramTTSService

tts = DeepgramTTSService(
    api_key=os.getenv("DEEPGRAM_API_KEY"),
    voice="aura-2-helena-en",
    sample_rate=24000,
    encoding="linear16",
)
```
