# AsyncAI TTS

```bash
pip install "piopiy-ai[asyncai]"
export ASYNCAI_API_KEY=your_key
```

### Parameters

- `api_key`: API key for authentication
- `voice_id`: Voice identifier to use
- `version`: API version (default `"v1"`)
- `url`: Endpoint URL (default `"wss://api.async.ai/text_to_speech/websocket/ws"`)
- `model`: Model name to use (default `"asyncflow_v2.0"`)
- `sample_rate`: Target audio sample rate
- `encoding`: Audio encoding (default `"pcm_s16le"`)
- `container`: Container type (default `"raw"`)
- `params`: Provider specific options
- `aggregate_sentences`: Aggregate sentences before synthesis (default `True`)


### Input Parameters

- `language`: Language for synthesis


### Example

```python
import os
from piopiy.services.asyncai.tts import AsyncAITTSService

tts = AsyncAITTSService(
    api_key=os.getenv("ASYNCAI_API_KEY"),
    voice_id="VOICE_ID",
    model="asyncflow_v2.0",
    sample_rate=24000,
    encoding="pcm_s16le",
)
```
