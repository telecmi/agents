# Cartesia TTS

```bash
pip install "piopiy-ai[cartesia]"
export CARTESIA_API_KEY=your_key
```

### Parameters

- `api_key`: API key for authentication
- `voice_id`: Voice identifier to use
- `cartesia_version`: Cartesia API version (default `"2025-04-16"`)
- `url`: Endpoint URL (default `"wss://api.cartesia.ai/tts/websocket"`)
- `model`: Model name to use (default `"sonic-2"`)
- `sample_rate`: Target audio sample rate
- `encoding`: Audio encoding (default `"pcm_s16le"`)
- `container`: Container type (default `"raw"`)
- `params`: Provider specific options
- `text_aggregator`: Custom text aggregator
- `aggregate_sentences`: Aggregate sentences before synthesis (default `True`)


### Input Parameters

- `language`: Language for synthesis
- `speed`: Voice speed control
- `emotion`: List of emotion tags (deprecated)


### Example

```python
import os
from piopiy.services.cartesia.tts import CartesiaTTSService

tts = CartesiaTTSService(
    api_key=os.getenv("CARTESIA_API_KEY"),
    voice_id="VOICE_ID",
    model="sonic-2",
    sample_rate=24000,
    encoding="pcm_s16le",
)
```
